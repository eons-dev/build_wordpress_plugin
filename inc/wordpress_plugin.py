import os
import logging
import shutil
import re
from ebbs import Builder

class wordpress_plugin(Builder):
    def __init__(this, name="Wordpress Plugin Builder"):
        super().__init__(name)

        this.clearBuildPath = True

        this.supportedProjectTypes.append("plugin")

        this.optionalKWArgs["plugin_name"] = None
        this.optionalKWArgs["description"] = None
        this.optionalKWArgs["version"] = "0.0.0"
        this.optionalKWArgs["author"] = "Web Infrastructure"
        this.optionalKWArgs["author_uri"] = "https://web.infrastructure.tech"
        this.optionalKWArgs["license"] = "MIT License"

    #Required Builder method. See that class for details.
    def Build(this):

        if (this.plugin_name is None):
            this.plugin_name = this.projectName

        if (this.description is None):
            this.description = f"Code for {this.projectName}"

        this.DetermineSuffix()

        this.targetIncPath = os.path.join(this.buildPath, "inc")
        try:
            logging.debug(f"copying {this.incPath} to {this.targetIncPath}")
            shutil.copytree(this.incPath, this.targetIncPath)
        except Exception as e:
            logging.debug(f"{e}")
        this.WriteMainFile()

    def DetermineSuffix(this):
        this.suffix = re.sub('[^A-Za-z0-9]+', '', this.projectName)

    def WriteMainFile(this):
        main_file = this.CreateFile(f"{this.projectName}.php")
        #NOTE: rglob from: https://stackoverflow.com/questions/17160696/php-glob-scan-in-subfolders-for-a-file
        main_file.write(
f'''<?php
/*
Plugin Name: {this.plugin_name}
Description: {this.description}
Version: {this.version}
Author: {this.author}
Author URI: {this.author_uri}
License: {this.license}
*/

function {this.suffix}_rglob($pattern, $flags = 0)
{{
    $files = glob($pattern, $flags); 
    foreach (glob(dirname($pattern).'/*', GLOB_ONLYDIR|GLOB_NOSORT) as $dir)
    {{
        $files = array_merge($files, {this.suffix}_rglob($dir.'/'.basename($pattern), $flags));
    }}
    return $files;
}}
function {this.suffix}_require_all()
{{
    foreach ({this.suffix}_rglob(dirname(__FILE__) . "/inc/*.php") as $filename)
    {{
        require_once($filename);
    }}
}}
add_action('init', '{this.suffix}_require_all');
''')
        main_file.close()
