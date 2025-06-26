#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import urllib.parse

def url_encode_path(path):
    """URL encode a file path, handling Greek characters and spaces"""
    # Replace backslashes with forward slashes
    path = path.replace('\\', '/')
    # Split path into components and encode each
    parts = path.split('/')
    encoded_parts = []
    for part in parts:
        if part:  # Skip empty parts
            encoded_part = urllib.parse.quote(part, safe='')
            encoded_parts.append(encoded_part)
    return '/'.join(encoded_parts)

def parse_directory_listing(file_path):
    """Parse the directory listing file and extract paths"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract directory paths and files
    directories = []
    files = []
    
    # Find all directory lines
    dir_pattern = r'Directory: C:\\Users\\dee\\Desktop\\SW PORTAL\\(.+)'
    dir_matches = re.findall(dir_pattern, content)
    
    # Split content by directory sections
    sections = re.split(r'Directory: C:\\Users\\dee\\Desktop\\SW PORTAL\\?', content)
    
    current_dir = ""
    for i, section in enumerate(sections):
        if i == 0:  # Skip first empty section
            continue
            
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        # Get directory path from first line
        dir_line = lines[0].strip()
        if dir_line:
            current_dir = dir_line
        else:
            current_dir = ""  # Root directory
            
        # Skip excluded directories
        if should_exclude_directory(current_dir):
            continue
            
        # Add directory to list if it's not root
        if current_dir and current_dir not in [d[0] for d in directories]:
            directories.append((current_dir, current_dir.split('\\')[-1]))
        
        # Parse files in this directory
        for line in lines[4:]:  # Skip header lines
            if line.strip() and not line.startswith('----') and not line.startswith('Mode'):
                # Extract file info
                parts = line.split()
                if len(parts) >= 4:
                    mode = parts[0]
                    if mode.startswith('-'):  # It's a file
                        filename = ' '.join(parts[3:])
                        if current_dir:
                            full_path = current_dir + '\\' + filename
                        else:
                            full_path = filename
                        files.append((full_path, filename))
                    elif mode.startswith('d'):  # It's a directory
                        dirname = ' '.join(parts[3:])
                        if current_dir:
                            full_path = current_dir + '\\' + dirname
                        else:
                            full_path = dirname
                        if not should_exclude_directory(full_path):
                            directories.append((full_path, dirname))
    
    return directories, files

def should_exclude_directory(path):
    """Check if directory should be excluded"""
    exclude_patterns = [
        'Manus01',
        'Follow Instructions in Pasted_Content',
        'Πλήρης Κατάλογος Αρχείων',
        'NEWS_FEEDS_SOURCES',
        'ΟΔΗΓΟΙ_ΕΦΑΡΜΟΓΗΣ'
    ]
    
    for pattern in exclude_patterns:
        if pattern in path:
            return True
    return False

def generate_html_links(directories, files):
    """Generate HTML links for directories and files"""
    html_content = []
    
    # Group by main categories
    categories = {
        'ΑΠΟΦΑΣΕΙΣ_ΑΔΕΙΟΔΟΤΗΣΗΣ': 'Αποφάσεις Αδειοδότησης',
        'ΑΠΟΦΑΣΕΙΣ_ΣΥΓΚΡΟΤΗΣΗΣ_ΕΠΙΤΡΟΠΩΝ_ΚΑΙ_ΚΟΙΝΩΝΙΚΟΥ_ΣΥΜΒΟΥΛΟΥ': 'Αποφάσεις Συγκρότησης Επιτροπών',
        'ΕΚΘΕΣΕΙΣ_ΕΛΕΓΧΩΝ': 'Εκθέσεις Ελέγχων',
        'ΕΚΠΑΙΔΕΥΤΙΚΟ_ΥΛΙΚΟ': 'Εκπαιδευτικό Υλικό',
        'ΕΝΤΥΠΑ_ΑΙΤΗΣΕΩΝ': 'Έντυπα Αιτήσεων',
        'ΝΟΜΟΘΕΣΙΑ_ΚΟΙΝΩΝΙΚΗΣ_ΜΕΡΙΜΝΑΣ': 'Νομοθεσία Κοινωνικής Μέριμνας',
        'ΤΗΛΕΦΩΝΙΚΟΙ_ΚΑΤΑΛΟΓΟΙ': 'Τηλεφωνικοί Κατάλογοι'
    }
    
    for category_key, category_title in categories.items():
        html_content.append(f'<h2>{category_title}</h2>')
        html_content.append('<div class="category-section">')
        
        # Add directories for this category
        category_dirs = [d for d in directories if d[0].startswith(category_key)]
        for dir_path, dir_name in sorted(category_dirs):
            encoded_path = url_encode_path(dir_path)
            html_content.append(f'<a href="/SW%20PORTAL/{encoded_path}/" target="_blank" class="folder-link">')
            html_content.append(f'<i class="fas fa-folder"></i> {dir_name}')
            html_content.append('</a>')
        
        # Add files for this category
        category_files = [f for f in files if f[0].startswith(category_key)]
        for file_path, file_name in sorted(category_files):
            encoded_path = url_encode_path(file_path)
            html_content.append(f'<a href="/SW%20PORTAL/{encoded_path}" target="_blank" class="file-link">')
            html_content.append(f'<i class="fas fa-file"></i> {file_name}')
            html_content.append('</a>')
        
        html_content.append('</div>')
    
    return '\n'.join(html_content)

def main():
    # Parse the directory listing
    directories, files = parse_directory_listing('/home/ubuntu/upload/SWPORTALDATA.txt')
    
    # Filter out excluded items
    filtered_dirs = [(d, n) for d, n in directories if not should_exclude_directory(d)]
    filtered_files = [(f, n) for f, n in files if not should_exclude_directory(f)]
    
    # Generate HTML
    html_links = generate_html_links(filtered_dirs, filtered_files)
    
    # Create complete HTML page
    html_page = f'''<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Πύλη Κοινωνικής Μέριμνας - Κατάλογος Αρχείων</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
    <style>
        .category-section {{
            margin-bottom: 2rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 0.5rem;
        }}
        .folder-link, .file-link {{
            display: block;
            padding: 0.5rem 1rem;
            margin: 0.25rem 0;
            background: white;
            border-radius: 0.375rem;
            text-decoration: none;
            color: #374151;
            transition: all 0.2s;
            border-left: 4px solid #3b82f6;
        }}
        .folder-link:hover, .file-link:hover {{
            background: #e5e7eb;
            transform: translateX(4px);
        }}
        .folder-link i {{
            color: #f59e0b;
            margin-right: 0.5rem;
        }}
        .file-link i {{
            color: #6b7280;
            margin-right: 0.5rem;
        }}
    </style>
</head>
<body class="bg-gray-50">
    <header class="bg-blue-900 text-white py-6 mb-8">
        <div class="container mx-auto px-6">
            <h1 class="text-3xl font-bold">Πύλη Κοινωνικής Μέριμνας</h1>
            <p class="text-blue-200">Κατάλογος Αρχείων με Απευθείας Συνδέσμους</p>
        </div>
    </header>
    
    <div class="container mx-auto px-6">
        {html_links}
    </div>
    
    <footer class="text-center text-gray-600 py-8 mt-12">
        <p>&copy; 2025 Πύλη Κοινωνικής Μέριμνας</p>
    </footer>
</body>
</html>'''
    
    # Save the HTML file
    with open('/home/ubuntu/portal_links.html', 'w', encoding='utf-8') as f:
        f.write(html_page)
    
    print("HTML file generated successfully!")
    print(f"Found {len(filtered_dirs)} directories and {len(filtered_files)} files")

if __name__ == "__main__":
    main()

