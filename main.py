def _get_images_information(self, image_list, path, image_layout_mapping):
        img_base64_list = []
        img_ids = []
        image_summaries = []
       
        # Iterate over the sorted list of files that are relevant
        for img_file in sorted(image_list):
            if img_file.endswith(".jpg"):
                img_path = os.path.join(path, img_file)
                id_key = "{}/{}/{}".format(self.client_id, self.index_name, uuid.uuid4())
                base64_image = self._encode_image(img_path)
               
                img_base64_list.append(base64_image)
                img_ids.append(id_key)


  data:image/jpeg;base64,
