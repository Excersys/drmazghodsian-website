import os
import re

# Directory containing your HTML files
HTML_DIR = "./"
# Directory where local assets are stored (relative to HTML root)
ASSETS_DIR = "assets"

# Regex for PatientPop asset URLs
PATIENTPOP_URL_RE = re.compile(r'https://(?:sa1s3optim|ui-cdn)\.patientpop\.com[^"\'\)>]+')

# Build mapping from PatientPop URLs to local asset paths
# Assumes assets were downloaded to assets/<...full path from URL...>
def build_url_to_local_map():
    url_to_local = {}
    for root, _, files in os.walk(os.path.join(HTML_DIR, ASSETS_DIR)):
        for file in files:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, HTML_DIR)
            # Reconstruct PatientPop URL from local path
            # Only for sa1s3optim and ui-cdn.patientpop.com
            if '/sa1s3optim.patientpop.com/' in rel_path or '/ui-cdn.patientpop.com/' in rel_path:
                continue  # skip if assets/sa1s3optim.patientpop.com/... structure exists (shouldn't for our script)
            # Guess URL based on rel_path after 'assets/'
            asset_subpath = rel_path[len(ASSETS_DIR)+1:]
            if asset_subpath:
                # Try both sa1s3optim and ui-cdn
                url1 = f"https://sa1s3optim.patientpop.com/{asset_subpath}"
                url2 = f"https://ui-cdn.patientpop.com/{asset_subpath}"
                url_to_local[url1] = rel_path
                url_to_local[url2] = rel_path
    return url_to_local

def patch_html_files(root_dir, url_to_local):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(subdir, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                new_content = content
                # Replace each PatientPop URL with its local equivalent
                for url, local_path in url_to_local.items():
                    new_content = new_content.replace(url, local_path)
                # Remove PatientPop preconnect/dns-prefetch links
                new_content = re.sub(r'<link[^>]+href="https://sa1s3optim.patientpop.com"[^>]*>', '', new_content)
                new_content = re.sub(r'<link[^>]+href="https://ui-cdn.patientpop.com"[^>]*>', '', new_content)
                # Remove any remaining PatientPop URLs (e.g. in comments, stray links)
                new_content = re.sub(r'https://(?:sa1s3optim|ui-cdn)\.patientpop\.com[^"\'\)>]+', '', new_content)
                if new_content != content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Patched {file_path}")

if __name__ == "__main__":
    url_to_local = build_url_to_local_map()
    patch_html_files(HTML_DIR, url_to_local)
