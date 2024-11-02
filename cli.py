# crandox/cli.py
import argparse
import sys
from pathlib import Path
from typing import List, Optional
import webbrowser
import shutil
from datetime import datetime
import json
from .dlcranv2 import CRANDownloader
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from rich.markdown import Markdown

console = Console()

class CRANDoxCLI:
    def __init__(self):
        self.downloader = CRANDownloader()
        self.config_file = Path.home() / '.crandox' / 'config.json'
        self.stats_file = Path.home() / '.crandox' / 'stats.json'
        self.init_config()

    def init_config(self):
        """Initialize configuration files"""
        self.config_file.parent.mkdir(exist_ok=True)
        if not self.config_file.exists():
            default_config = {
                "storage_path": str(Path.home() / "crandox_docs"),
                "auto_update": True,
                "max_concurrent_downloads": 5,
                "preferred_format": "pdf"
            }
            self.config_file.write_text(json.dumps(default_config))

    def stats(self):
        """Show download statistics"""
        downloaded = self.downloader.get_downloaded_packages()
        total = len(self.downloader.get_package_list())
        size = sum(p.stat().st_size for p in Path("dox").glob("*.pdf"))
        
        table = Table(title="CRAN Documentation Statistics")
        table.add_row("Total Packages", str(total))
        table.add_row("Downloaded", str(len(downloaded)))
        table.add_row("Storage Used", f"{size/1024/1024:.2f} MB")
        console.print(table)

    def export_list(self, format: str = "csv"):
        """Export package list to CSV/JSON"""
        packages = self.downloader.get_package_list()
        if format == "csv":
            with open("packages.csv", "w") as f:
                f.write("\n".join(packages))
        elif format == "json":
            with open("packages.json", "w") as f:
                json.dump({"packages": packages}, f)

    def check_updates(self):
        """Check for package updates"""
        current = set(self.downloader.get_downloaded_packages())
        available = set(self.downloader.get_package_list())
        updates = available - current
        return updates

    def cleanup(self, days: int = 30):
        """Remove old unused documentation"""
        now = datetime.now()
        removed = 0
        for pdf in Path("dox").glob("*.pdf"):
            age = (now - datetime.fromtimestamp(pdf.stat().st_mtime)).days
            if age > days:
                pdf.unlink()
                removed += 1
        return removed

    def validate_docs(self):
        """Validate downloaded documentation"""
        invalid = []
        for pdf in Path("dox").glob("*.pdf"):
            if pdf.stat().st_size < 1000:  # Simple size check
                invalid.append(pdf.name)
        return invalid

    def open_doc(self, package: str):
        """Open documentation in default PDF viewer"""
        pdf_path = Path("dox") / f"{package}.pdf"
        if pdf_path.exists():
            webbrowser.open(str(pdf_path))
        else:
            console.print(f"[red]Documentation for {package} not found[/red]")

    def download_packages(self, packages: Optional[List[str]] = None, force: bool = False) -> None:
        """Download specific packages or all if none specified"""
        all_packages = self.downloader.get_package_list()
        
        if packages:
            to_download = [p for p in packages if p in all_packages]
            if not to_download:
                console.print("[red]No valid packages specified[/red]")
                return
        else:
            to_download = all_packages

        with Progress() as progress:
            task = progress.add_task("[green]Downloading...", total=len(to_download))
            for pkg in to_download:
                if self.downloader.download_package(pkg):
                    progress.advance(task)

    def search(self, query: str) -> None:
        """Search for packages matching query"""
        all_packages = self.downloader.get_package_list()
        matches = [p for p in all_packages if query.lower() in p.lower()]
        
        table = Table(title=f"Search results for: {query}")
        table.add_column("Package")
        
        for pkg in matches:
            table.add_row(pkg)
        
        console.print(table)

    def list_packages(self) -> None:
        """List all available packages"""
        packages = self.downloader.get_package_list()
        downloaded = self.downloader.get_downloaded_packages()
        
        table = Table(title="CRAN Packages")
        table.add_column("Package")
        table.add_column("Status")
        
        for pkg in packages:
            status = "[green]Downloaded[/green]" if pkg in downloaded else "[yellow]Available[/yellow]"
            table.add_row(pkg, status)
            
        console.print(table)

def main():
    parser = argparse.ArgumentParser(description="CRAN documentation manager")
    parser.add_argument("--download", "-d", nargs="*", help="Download packages")
    parser.add_argument("--force", "-f", action="store_true", help="Force download")
    parser.add_argument("--search", "-s", help="Search packages")
    parser.add_argument("--list", "-l", action="store_true", help="List packages")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--export", choices=["csv", "json"], help="Export package list")
    parser.add_argument("--cleanup", type=int, help="Remove docs older than N days")
    parser.add_argument("--validate", action="store_true", help="Validate downloads")
    parser.add_argument("--open", help="Open package documentation")
    parser.add_argument("--check-updates", action="store_true", help="Check updates")

    args = parser.parse_args()
    cli = CRANDoxCLI()

    if args.stats:
        cli.stats()
    elif args.export:
        cli.export_list(args.export)
    elif args.cleanup:
        removed = cli.cleanup(args.cleanup)
        console.print(f"Removed {removed} old files")
    elif args.validate:
        invalid = cli.validate_docs()
        console.print(f"Found {len(invalid)} invalid files")
    elif args.open:
        cli.open_doc(args.open)
    elif args.check_updates:
        updates = cli.check_updates()
        console.print(f"Found {len(updates)} packages to update")
    elif args.download is not None:
        cli.download_packages(args.download, args.force)
    elif args.search:
        cli.search(args.search)
    elif args.list:
        cli.list_packages()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()