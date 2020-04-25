from shutil import copy2

import os
import sys
import datetime
import json

from Post import MDF

def preparing_file_list (base_path, content_list) :
    image_files_path = []
    markdown_file_path = []

    for content in content_list :
        if not os.path.isdir(os.path.join(base_path,content)):
            continue

        file_list = os.listdir(os.path.join(base_path, content))
        for filename in file_list :
            # Check for file extension
            file_parts = filename.split('.')
            final_file_path = os.path.join(base_path, content, filename)
            
            if len(file_parts) > 1 :
                # Markdown Extension
                if file_parts[-1] == "md" :
                    markdown_file_path.append(final_file_path)
                # Other categorise to image
                else :
                    image_files_path.append(final_file_path)
    
    return markdown_file_path, image_files_path           

def write_json_to_destination (destination_path, posts, post_tag, tags) :
    dump_posts = []

    for post in posts :
        dump_posts.append(post.serialise())

    json_dump = {
        "db" :[
            {
                "meta" :
                {
                    "exported_on" : datetime.datetime.now().timestamp(),
                    "version" : "3.13.4"
                },
                "data" :
                {
                    "posts" : dump_posts,
                    "tags" : tags,
                    "posts_tags" : post_tag
                }

            }
        ]
    }

    destination_file = open(os.path.join(destination_path, 'data.json'), 'w')
    destination_file.write(json.dumps(json_dump, ensure_ascii=False))
    destination_file.close()

    return json_dump
# Image Helper Functions
def configurating_image_path (destination_path) :
    # Create base folder for images
    if not os.path.exists(os.path.join(destination_path, 'content')) :
        os.makedirs(os.path.join(destination_path, 'content'))

def convert_to_valid_month_format (input_month) :
    if len(str(input_month)) == 1 :
        return "0" + str(input_month)
    else :
        return str(input_month)

def create_image_path_convertor (image_file_path, destination_path) :
    # Convert from Original to New Path
    image_path_convertor = dict()

    for image_file in image_file_path :
        file_create_datetime = datetime.datetime.fromtimestamp(os.stat(image_file).st_ctime)        
        new_path = os.path.join('/content/images', str(file_create_datetime.year), convert_to_valid_month_format(file_create_datetime.month), image_file.split('/')[-1])
        image_path_convertor[image_file] = new_path

    return image_path_convertor

def create_image_file_name_to_path (image_path_convertor) :
    image_file_name_to_path = dict()

    for new_path in image_path_convertor.values() :
        image_file_name_to_path[new_path.split('/')[-1]] = new_path
    return image_file_name_to_path

def image_mover (image_path_convertor) :
    for source in image_path_convertor.keys() :
        os.makedirs(os.path.dirname(image_path_convertor[source]), exist_ok=True)
        copy2(source, image_path_convertor[source])

# Markdown Helper Function
def process_markdown (markdown_file_path_list, image_path_convertor) :
    posts = []
    tag_cloud = {}

    # Tag Cloud slug -> {name: tag_name, asso_posts: [1,2,3,4]}}

    for MD_path in markdown_file_path_list :
        current_post = MDF(MD_path, image_path_convertor).post
        current_post.assign_id(len(posts)+1)

        # Create Non-Exist Tag
        for tag in current_post.tags :
            tag_slug = tag.replace(' ' , '-').lower()

            # Not Exist -> Create New One
            if tag_slug not in tag_cloud :
                tag_cloud[tag_slug] = {
                    "id" : len(tag_cloud)+1,
                    "name" : tag,
                    "asso_posts" : []
                }
            
            # Save in asso_posts
            tag_cloud[tag_slug]['asso_posts'].append(current_post.id)
        posts.append(current_post)
    
    return posts,tag_cloud
    
# Tag Helper Function
def get_tags (tag_cloud) :
    final_tags = []

    for slug in tag_cloud.keys() :
        current_tag = {
            "id" : tag_cloud[slug]['id'],
            "name": tag_cloud[slug]['name'],
            "slug": slug
        }
        final_tags.append(current_tag)
    return final_tags

def get_post_tag (tag_cloud) :
    final_post_tag = []

    for slug in tag_cloud.keys() :
        current_tag = tag_cloud[slug]

        for post_id in current_tag['asso_posts']:
            final_post_tag.append({
                "id": len(final_post_tag)+1,
                "post_id": post_id,
                "tag_id" : current_tag['id']
            })

    return final_post_tag
def main (args) :
    base_path = args[1]
    destination_path = args[2]

    configurating_image_path(destination_path)
    content_list = os.listdir(base_path)
    markdown_file_path, image_file_path = preparing_file_list(base_path, content_list)

    print("There are " + str(len(content_list)) + " contents , " + str(len(markdown_file_path)) + " Markdown(s) with " + str(len(image_file_path)) + " image(s) to be converted")

    # Image Management
    image_path_convertor = create_image_path_convertor(image_file_path, destination_path)

    # image_mover(image_path_convertor)
    # print(str(len(image_path_convertor)) + " files has been moved.")

    # Markdown File Management
    posts, tag_cloud = process_markdown(markdown_file_path, create_image_file_name_to_path(image_path_convertor))
    write_json_to_destination (destination_path, posts, get_post_tag(tag_cloud), get_tags(tag_cloud))
    
if __name__ == "__main__":
    main(sys.argv)
