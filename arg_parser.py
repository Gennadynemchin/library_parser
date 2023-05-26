import argparse


def get_arg_parser():
    parser = argparse.ArgumentParser(description="Book parser tululu.org")
    parser.add_argument('--start_page', type=int, required=True, help='Start page for download')
    parser.add_argument('--end_page', type=int, required=False, help='Last page for download')
    parser.add_argument('--dest_folder', type=str, default='media')
    parser.add_argument('--json_path', type=str, default='json')
    parser.add_argument('--skip_imgs', action='store_true')
    parser.add_argument('--skip_txt', action='store_true')
    args = parser.parse_args()
    return args
