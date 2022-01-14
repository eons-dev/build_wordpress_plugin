import os
import logging
import shutil
import jsonpickle
from pathlib import Path
from ebbs import Builder

class wordpress_plugin(Builder):
    def __init__(self, name="Wordpress Plugin Builder"):
        super().__init__(name)

        self.clearBuildPath = True

        self.supportedProjectTypes.append("plugin")

        self.optionalKWArgs["plugin_name"] = None
        self.optionalKWArgs["description"] = None
        self.optionalKWArgs["version"] = "0.0.0"
        self.optionalKWArgs["author"] = "Web Infrastructure"
        self.optionalKWArgs["author_uri"] = "https://web.infrastructure.tech"
        self.optionalKWArgs["license"] = "MIT License"

    #Required Builder method. See that class for details.
    def Build(self):

        if (self.plugin_name is None):
            self.plugin_name = self.projectName

        if (self.description is None):
            self.description = f"Code for {self.projectName}"

        self.targetIncPath = os.path.join(self.buildPath, "inc")
        Path(self.targetIncPath).mkdir(parents=True, exist_ok=True)
        try:
            shutil.copytree(self.incPath, self.targetIncPath)
        except shutil.Error as exc:
            errors = exc.args[0]
            for error in errors:
                src, dst, msg = error
                logging.debug(f"{msg}")
        self.WriteMainFile()
        logging.info("Complete!")

    def WriteMainFile(self):
        main_file = self.CreateFile(f"{self.projectName}.php")
        #NOTE: rglob from: https://stackoverflow.com/questions/17160696/php-glob-scan-in-subfolders-for-a-file
        main_file.write(
f'''<?php
/*
Plugin Name: {self.plugin_name}
Description: {self.description}
Version: {self.version}
Author: {self.author}
Author URI: {self.author_uri}
License: {self.license}
*/

function {self.projectName}_rglob($pattern, $flags = 0)
{{
    $files = glob($pattern, $flags); 
    foreach (glob(dirname($pattern).'/*', GLOB_ONLYDIR|GLOB_NOSORT) as $dir)
    {{
        $files = array_merge($files, {self.projectName}_rglob($dir.'/'.basename($pattern), $flags));
    }}
    return $files;
}}
function {self.projectName}_require_all()
{{
    foreach ({self.projectName}_rglob(dirname(__FILE__) . "/inc/*.php") as $filename)
    {{
        require_once($filename);
    }}
}}
add_action('init', '{self.projectName}_require_all');
''')
        main_file.close()
