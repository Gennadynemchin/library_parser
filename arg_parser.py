import argparse


def get_arg_parser(default_end_page):
    parser = argparse.ArgumentParser(description="Book parser tululu.org")
    parser.add_argument('--start_page', type=int, required=True, help='Start page for download')
    parser.add_argument('--end_page', type=int, default=default_end_page, required=False, help='Last page for download')
    parser.add_argument('--dest_folder', type=str, default='media', help='Destination folder for text and covers')
    parser.add_argument('--json_path', type=str, default='json', help='Destination folder for json file')
    parser.add_argument('--skip_imgs', action='store_true', help='Book covers will not be downloaded')
    parser.add_argument('--skip_txt', action='store_true', help='Book text will not be downloaded')
    args = parser.parse_args()
    return args
