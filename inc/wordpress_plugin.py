import os
import logging
import shutil
import jsonpickle
from distutils.file_util import copy_file
from distutils.dir_util import copy_tree, mkpath
from ebbs import Builder

class wordpress_plugin(Builder):
    def __init__(self, name="Wordpress Plugin Builder"):
        super().__init__(name)
    
        self.supportedProjectTypes.append("plugin")

    #Required Builder method. See that class for details.
    def Build(self):
        #get config info
        config_file = open(os.path.join(self.rootPath, "config.json"), "r")
        self.config = jsonpickle.decode(config_file.read())

        if os.path.exists(self.buildPath):
            logging.info(f"DELETING {self.buildPath}")
            shutil.rmtree(self.buildPath)

        self.buildPath = os.path.abspath(os.path.join(self.buildPath, self.projectName))
        logging.info(f"Using build path {self.buildPath}")
        mkpath(self.buildPath)
        mkpath(os.path.join(self.buildPath,"inc"))
        copy_tree(self.incPath, os.path.join(self.buildPath,"inc"))
        os.chdir(self.buildPath)
        self.WriteMainFile()
        os.chdir(os.path.join(self.rootPath)
        shutil.make_archive(self.projectName, 'zip', self.buildPath)
        logging.info("Complete!")

    def WriteMainFile(self):
        main_file = self.CreateFile(f"{self.projectName}.php")
        #NOTE: rglob from: https://stackoverflow.com/questions/17160696/php-glob-scan-in-subfolders-for-a-file
        main_file.write(
f'''<?php
/*
Plugin Name: {self.config["Plugin Name"]}
Description: {self.config["Description"]}
Version: {self.config["Version"]}
Author: {self.config["Author"]}
Author URI: {self.config["Author URI"]}
License: {self.config["License"]}
*/

function rglob($pattern, $flags = 0)
{{
    $files = glob($pattern, $flags); 
    foreach (glob(dirname($pattern).'/*', GLOB_ONLYDIR|GLOB_NOSORT) as $dir)
    {{
        $files = array_merge($files, rglob($dir.'/'.basename($pattern), $flags));
    }}
    return $files;
}}
function require_all()
{{
    foreach (rglob(dirname(__FILE__) . "/inc/*.php") as $filename)
    {{
        require_once($filename);
    }}
}}
add_action('init', 'require_all');
''')
        main_file.close()
