import json
import datetime

class Post: 
    def __init__(self, id=1, title="title", slug="slug", markdown="content", excerpt="excerpt"):
        super().__init__()
        self.id = id
        self.title = title
        self.slug = slug
        self.markdown = markdown
        self.excerpt = excerpt
        self.tags = []

    def add_tag (self, new_tag_name) :
        if new_tag_name not in self.tags :
            self.tags.append(new_tag_name)

    def convert_tag_to_id (self, tag_dict) :
        new_tags = []

        for tag in self.tags :
            new_tags.append(tag_dict[tag])
        self.tags = new_tags

    def assign_id (self, id) :
        self.id = id

    def serialise (self) :
        post_dump = {
            "id":            self.id,
            "title":         self.title,
            "slug":          self.slug,
            "mobiledoc" :    json.dumps({
                "version" : "0.3.1",
                "atoms" : [],
                "cards" : [],
                "markups" : [],
                "sections" : []
            }),
            "feature_image": getattr(self, 'feature_image', None),
            "featured":      getattr(self, 'featured', 0), 
            "page":          getattr(self, 'is_page', 0),
            "status":        getattr(self, 'is_published', "published"),
            "published_at":  getattr(self, 'publish_date', datetime.datetime.now().timestamp()),
            "published_by":  getattr(self, 'author', 1),
            "meta_title":    self.title,
            "meta_description":getattr(self, 'excerpt', None),
            "author_id":     getattr(self, 'author', 1),
            "created_at":    getattr(self, 'publish_date', datetime.datetime.now().timestamp()),
            "created_by":    getattr(self, 'author', 1),
            "updated_at":    getattr(self, 'publish_date', datetime.datetime.now().timestamp()),
            "updated_by":    getattr(self, 'author', 1),
            "custom_excerpt":getattr(self, 'excerpt', None),
            "markdown": self.markdown, 
        }

        return post_dump

class MDF :
    def convert_content (self, content, image_dict) :
        content_line = content.split('\n')
        convert_content = ""

        for line in content_line :
            if line[0:1] == "![" :
                # Image Tag -> Example ![Docker Hub](./install_unifi_controller_docker_2.png)
                # Let's Extract the components
                alt = line.split(']')[0][2:]
                img_path = line.split(']')[1][3:-1]

                convert_content = "![" + alt + "](" + img_path + ")\n"
            else :
                convert_content += line + "\n"
        
        return convert_content

    def __init__(self, file_path, img_dictionary):
        self.file_pointer = open(file_path, 'r')

        file_components = self.file_pointer.read().split('---')[1:]
        
        content = file_components[1]

        self.post = Post()

        # Trim line breaking on the first char of content
        if content[0] == "\n" :
            content = content[1:]

        self.post.markdown = self.convert_content(content, img_dictionary)

        # Metadata Decomposition
        metadata_list = file_components[0].split("\n")

        for metadata in metadata_list :
            decomposed_meta = metadata.split(':')
            
            if len(decomposed_meta) < 2 :
                continue

            decomposed_meta[0] = decomposed_meta[0].replace(' ', '')

            if decomposed_meta[0] == 'title' :
                self.post.title = decomposed_meta[1].replace('"', '')
            
            elif decomposed_meta[0] == 'image' and len(decomposed_meta[1].replace(' ', '')) > 0:
                if len(decomposed_meta[1].split('/')) > 1 :
                    feature_image_name = decomposed_meta[1].split('/')[-1]
                else :
                    feature_image_name = decomposed_meta[1]
                
                if feature_image_name in img_dictionary :
                    self.post.feature_image = img_dictionary[feature_image_name.replace('"', '').replace('./', '').replace(' ' ,'')]
            
            elif decomposed_meta[0] == 'category' :
                category_name = decomposed_meta[1].replace('"', '')
                if category_name[0] == " " :
                    category_name = category_name[1:]
                
                if category_name[-1] == " " :
                    category_name = category_name[:-1]
                    
                self.post.add_tag(category_name)
            
            elif decomposed_meta[0] == 'excerpt' :
                self.post.excerpt = decomposed_meta[1].replace('"', '')
            
            elif decomposed_meta[0] == 'date' :
                self.post.excerpt = int(datetime.datetime.strptime(decomposed_meta[1].replace(' ', '').replace('"', '').split('T')[0], '%Y-%m-%d').timestamp())
            
            elif decomposed_meta[0] == 'is_page' :
                self.post.page = 0 if decomposed_meta[1] == "post" else 1
            
            elif decomposed_meta[0] == 'featured' :
                self.post.featured = 0 if "false" in decomposed_meta else 1
            
            elif decomposed_meta[0] == 'status' :
                self.post.is_published = decomposed_meta[1].replace(' ', '')

        self.file_pointer.close()