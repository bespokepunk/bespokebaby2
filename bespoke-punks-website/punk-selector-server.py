#!/usr/bin/env python3
"""
Simple server for punk selector UI
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
from datetime import datetime

class PunkSelectorHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/punks':
            # Return list of all punk PNG files
            punks_dir = '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/Aseperite/all'
            files = [f.replace('.png', '') for f in os.listdir(punks_dir) if f.endswith('.png')]
            files.sort()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(files).encode())
        elif self.path.startswith('/punks/'):
            # Serve punk images
            punk_name = self.path.replace('/punks/', '')
            punk_path = f'/Users/ilyssaevans/Documents/GitHub/bespokebaby2/Aseperite/all/{punk_name}'

            try:
                with open(punk_path, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.end_headers()
                    self.wfile.write(f.read())
            except:
                self.send_response(404)
                self.end_headers()
        else:
            # Serve the HTML file
            if self.path == '/':
                self.path = '/punk-selector.html'
            return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/generate-prompts':
            # Read the selected punks
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())

            selected_punks = data.get('punks', [])

            # Generate prompts file for selected punks only
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'SELECTED_PROMPTS_{timestamp}.md'
            output_path = os.path.join('/Users/ilyssaevans/Documents/GitHub/bespokebaby2/bespoke-punks-website', output_file)

            with open(output_path, 'w') as f:
                f.write(f"# Selected Punks Prompts ({len(selected_punks)} punks)\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")

                for punk in selected_punks:
                    f.write(f"## {punk}\n\n")
                    f.write("**Prompt:** [TO BE WRITTEN - Add character notes and craft compelling world]\n\n")
                    f.write("**Character Notes:**\n")
                    f.write("- Role/Identity:\n")
                    f.write("- Visual Traits:\n")
                    f.write("- Personality:\n")
                    f.write("- World Vibe:\n\n")
                    f.write("---\n\n")

            # Return success
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'success': True,
                'count': len(selected_punks),
                'filename': output_file
            }
            self.wfile.write(json.dumps(response).encode())

def run_server(port=8080):
    os.chdir('/Users/ilyssaevans/Documents/GitHub/bespokebaby2/bespoke-punks-website')
    server_address = ('', port)
    httpd = HTTPServer(server_address, PunkSelectorHandler)
    print(f'\n✅ Punk Selector running at: http://localhost:{port}\n')
    print(f'   Open this URL in your browser to select punks!\n')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
