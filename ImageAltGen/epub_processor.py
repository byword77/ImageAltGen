# -*- coding: utf-8 -*-
try:
    from sigil_bs4 import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
import posixpath
import urllib.parse
import re

class EpubProcessor:
    def __init__(self, bk):
        self.bk = bk

    def extract_images_from_text(self):
        images_info = []
        for (id, href) in self.bk.text_iter():
            html_data = self.bk.readfile(id)
            html = html_data if isinstance(html_data, str) else html_data.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find <img> tags
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if not src:
                    continue
                # resolve relative href to find manifest id
                src_clean = urllib.parse.unquote(src.split('#')[0])
                base_dir = posixpath.dirname(href)
                img_href = posixpath.normpath(posixpath.join(base_dir, src_clean))
                
                img_id = self.bk.href_to_id(img_href)
                if not img_id:
                    # fallback in case src is already absolute to root
                    img_id = self.bk.href_to_id(src_clean)
                
                if not img_id:
                    continue
                
                alt_text = img.get('alt', '')
                role_val = img.get('role', 'img') # epub3 role
                
                images_info.append({
                    "html_id": id,
                    "html_href": href,
                    "img_id": img_id,
                    "src": src,
                    "alt": alt_text,
                    "role": role_val,
                    "tag_type": "img"
                })
                
            # Find <svg><image> tags
            for svg_img in soup.find_all('image'):
                src = svg_img.get('xlink:href', '') or svg_img.get('href', '')
                if not src:
                    continue
                src_clean = urllib.parse.unquote(src.split('#')[0])
                base_dir = posixpath.dirname(href)
                img_href = posixpath.normpath(posixpath.join(base_dir, src_clean))
                
                img_id = self.bk.href_to_id(img_href)
                if not img_id:
                    img_id = self.bk.href_to_id(src_clean)
                
                if not img_id:
                    continue
                    
                images_info.append({
                    "html_id": id,
                    "html_href": href,
                    "img_id": img_id,
                    "src": src,
                    "alt": svg_img.get('alt', ''), # alt inside title/desc usually, but let's read alt attribute directly just in case or skip
                    "role": svg_img.get('role', 'img'),
                    "tag_type": "svg_image"
                })
        
        # Deduplicate while preserving order (some images may appear multiple times)
        # We'll allow duplicates because they are in different contexts
        return images_info

    def get_image_data(self, img_id):
        return self.bk.readfile(img_id)

    def apply_to_epub(self, images_info, update_accessibility_meta, meta_text):
        # Group changes by html file to modify once per file
        changes_by_html = {}
        for info in images_info:
            html_id = info["html_id"]
            if html_id not in changes_by_html:
                changes_by_html[html_id] = []
            changes_by_html[html_id].append(info)
            
        for html_id, edits in changes_by_html.items():
            html_data = self.bk.readfile(html_id)
            html = html_data if isinstance(html_data, str) else html_data.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            
            for edit in edits:
                # find the correct element
                if edit["tag_type"] == "img":
                    for img in soup.find_all('img'):
                        if img.get('src') == edit["src"]:
                            img['alt'] = edit["alt"]
                            if self.bk.epub_version() == "3.0" and edit["role"]:
                                img['role'] = edit["role"]
                elif edit["tag_type"] == "svg_image":
                    for svg_img in soup.find_all('image'):
                        src = svg_img.get('xlink:href', '') or svg_img.get('href', '')
                        if src == edit["src"]:
                            if not svg_img.find('title'):
                                title_tag = soup.new_tag('title')
                                svg_img.insert(0, title_tag)
                            svg_img.find('title').string = edit["alt"]
                            if self.bk.epub_version() == "3.0" and edit["role"]:
                                svg_img['role'] = edit["role"]
                                
            updated_html = str(soup)
            self.bk.writefile(html_id, updated_html)
            
        if self.bk.epub_version() == "3.0" and update_accessibility_meta and meta_text:
            opf_xml = self.bk.get_opf()
            soup = BeautifulSoup(opf_xml, 'xml')
            metadata = soup.find('metadata')
            if metadata:
                # Add text snippet as nodes to metadata
                try:
                    meta_soup = BeautifulSoup(f"<wrapper>{meta_text}</wrapper>", 'xml')
                    wrapper = meta_soup.find('wrapper')
                    elements = list(wrapper.contents) if wrapper else list(meta_soup.contents)
                    for element in elements:
                        if element.name == 'meta' and element.get('property'):
                            prop = element.get('property')
                            val = element.string
                            # check for duplicate
                            existings = metadata.find_all('meta', property=prop)
                            if any(ex.string == val for ex in existings):
                                continue
                        elif element.name is None and (not element.string or not element.string.strip()):
                            continue
                        metadata.append(element)
                except:
                    # simplistic fallback
                    pass
                self.bk.setmetadataxml(str(metadata))
