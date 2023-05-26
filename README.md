# Book parser tutulu.org

### How to install

```
git clone https://github.com/Gennadynemchin/library_parser.git
```

Install requested libraries:
```
pip install requirements.txt
```

### How to start

You have to use arguments while you are running the script. Example:
```
python main.py --start_page 10 --end_page 20
```
After running the script downloading books from page numer 10 to page 30.

Choose name of destination folder for books and images:
```commandline
--dest_folder
```
Choose name of destination folder for json file:
```commandline
--json_path
```
Download without book covers:
```commandline
--skip_imgs
```
Download without book text:
```commandline
--skip_txt
```