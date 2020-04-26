# Gatsby2Ghost

**Gatsby2Ghost** is simple Python script that content convertor from gatsby markdown to Ghost import compatible json file. 

## Requirement

The content must placed in the following format

```
\
    content_1
        index.md
        image_x.jpg
    content_2
        index.md
        image.png
```

Moreover, the format in the markdown file is specific in the following format

```
---
title: "<your_title_here>"
image: "<your_thumbnail_path>"
excerpt: "<your excerpt>"
date: <datetime in this format <year-month-dayT00:00:00.000Z>
isFeatured: <isFeature post true|false>
status: <post_status published|draft>
---

<content in markdown format>
	

```

## Installation

There is no installation require just clone this repository, please be make sure that Python 3 has been installed on your machine and run the script by using the following command

```
python main.py <root_content_path> <destination_path>
```

The script will look for markdown and image in the source folder, it will convert into Ghost compatible json file and sort the image into folders.