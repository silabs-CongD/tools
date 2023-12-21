# Author Cong Do
import os
import sys
import re
import argparse

# Guide to use
# python arduino_cli.py --arduino_cli "D:/Tools/arduino-cli/arduino-cli" --arduino_lib "D:/Workspace/arduino/arduino-silabs" --projects "ezble" --board "xg24explorerkit"
# Output folder will be in path of file arduino_cli.py.

##########################################################################################
def execute_compile(arduino_cli, board_fqbn, project_file_path, project_out_dir, compile_log):
    compile_command = arduino_cli + " compile --fqbn " + board_fqbn + " " + project_file_path + " --output-dir " + project_out_dir + " --log-level warn --warnings all >> " + compile_log + " 2>&1"
    os.system(compile_command) 

# Analysis compile log
def analysys_log(project_out_dir, compile_log):
    error_log = []
    f = open(compile_log, "r")
    for line in f:
        if line.find("warning:") != -1 or line.find("Warning:") != -1:
            # print("Error compile !!!")
            error_log.append(line + "\n")
            return False
            
    # Remove un-used files, keep .hex
    f.close()
    for root, dirs, files in os.walk(project_out_dir):
        for file in files:
            if file.find(".hex") == -1 and file.find("compile.log") == -1:
                file_path = root + "/" + file
                os.remove(file_path)          

def generate_html(out_root_dir, project_list, board_list, status_build):
    content = """<!DOCTYPE html>
    <html>
    <head>
    <style>
    body {
    font-family: Helvetica, sans-serif;
    font-size: 0.9em;
    color: black;
    padding: 6px;
    }
    table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
    }
    td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
    }
    tr:nth-child(even) {
    background-color: #dddddd;
    }
    </style>
    </head>
    <body>
    <h1>Build Test Project</h1>
    <p>Please log Jira ticket or send email to me if you got any issue: <b>cong.do@silabs.com</b> Thanks!</p>
    <h2>Summary Table</h2>
    <table>
    <tr>
    <th>No</th>
    <th>Project Name</th>
    <th>Status</th>
    <th>Board Id</th>
    </tr>
    """	
    report_id = 0
    for report_id in range(len(status_build)):
        content += "<tr><td>{}</td>".format(report_id)
        content += "<td>{}</td>".format(project_list[report_id])
        if status_build[report_id] == False:
            content += "<td style=\"background-color:red;\">Fail</td>"
        else:
            content += "<td style=\"background-color:green;\">Pass</td>"
        content += "<td>{}</td></tr>".format(board_list[report_id])
    
    content += "</ul></body></html>"
    # Write content to file
    f = open(out_root_dir + "/compile_project.html", "w")
    f.write(content)
    f.close() 

# ############################## execute compile projects

def compile_project(arduino_cli, example_root_dir_list, variant_input, out_root_dir):
    for example_root_dir in example_root_dir_list:
        tmp = os.path.dirname(example_root_dir)
        app_name = os.path.basename(tmp)#ArduinoBLE, ezBLE, Matter ... etc

        project_path_list = []
        # Create output compile dir
        app_out_dir = os.path.join(out_root_dir, app_name)
        app_out_dir = app_out_dir.replace("\\", "/")
        os.mkdir(app_out_dir)
        for root, dirs, files in os.walk(example_root_dir):
            for file in files:
                if file.find(".ino") != -1:
                    project_path_list.append(root + "/" + file)
        
        # compile
        board_fqbn_list = []
        # Got variant name, this name depend on local folder name of other PC, so it different
        os.system(arduino_cli + " board listall xg24 >> variant.log")
        var_log = open("variant.log", "r")
        for line in var_log:
            if line.find("xg24explorerkit") != -1:
                tmp = re.search("\s+([a-z0-9:]+):xg24explorerkit", line)
                if tmp:
                    variant_root = tmp.group(1)
                    # print("variant is:", variant_root, "\n")
                    break
        var_log.close()
        
        # Got project input
        if variant_input == "all":
            if app_name == "ezBLE" or app_name == "SiliconLabs":
                board_fqbn_list.append(variant_root + ":xg24explorerkit")
                board_fqbn_list.append(variant_root + ":xg24explorerkit_precomp")

                board_fqbn_list.append(variant_root + ":xg27devkit")
                board_fqbn_list.append(variant_root + ":xg27devkit_precomp")

                board_fqbn_list.append(variant_root + ":thingplusmatter_ble")
                board_fqbn_list.append(variant_root + ":thingplusmatter_ble_precomp")      
            
                board_fqbn_list.append(variant_root + ":bgm220explorerkit")
                board_fqbn_list.append(variant_root + ":bgm220explorerkit_precomp")

            elif app_name == "Matter":
                board_fqbn_list.append(variant_root + ":xg24explorerkit_matter")
                board_fqbn_list.append(variant_root + ":xg24explorerkit_matter_precomp")

                board_fqbn_list.append(variant_root + ":thingplusmatter_matter")
                board_fqbn_list.append(variant_root + ":thingplusmatter_matter_precomp")
            
            elif app_name == "Builtin":
                board_fqbn_list.append(variant_root + ":thingplusmatter_ble")
                board_fqbn_list.append(variant_root + ":thingplusmatter_ble_precomp")

                board_fqbn_list.append(variant_root + ":xg24explorerkit")
                board_fqbn_list.append(variant_root + ":xg24explorerkit_precomp")

                board_fqbn_list.append(variant_root + ":xg27devkit")
                board_fqbn_list.append(variant_root + ":xg27devkit_precomp")

                board_fqbn_list.append(variant_root + ":bgm220explorerkit")
                board_fqbn_list.append(variant_root + ":bgm220explorerkit_precomp")

                board_fqbn_list.append(variant_root + ":xg24explorerkit_matter")
                board_fqbn_list.append(variant_root + ":xg24explorerkit_matter_precomp")

                board_fqbn_list.append(variant_root + ":thingplusmatter_matter")
                board_fqbn_list.append(variant_root + ":thingplusmatter_matter_precomp")                
            else:
                print("Error. Arduino project not defined !!!\n")
                sys.exit(1)
        else:
            board_fqbn_list.append(variant_root + ":" + variant_input)
        
        status_build = []
        board_name_list = []
        sub_path_list = []
        for project_path in project_path_list:
            # Create sub folder of each project
            tmp1 = os.path.dirname(project_path)
            tmp2 = tmp1.split(example_root_dir)
            
            for board_fqbn in board_fqbn_list:
                # For Window Os
                sub_path = tmp2[1].replace("\\", "/")                
                sub_path_list.append(app_name + "/" + sub_path)

                board_name = board_fqbn.split(variant_root + ":")
                board_name = board_name[1]
                board_name_list.append(board_name)

                project_out_dir = app_out_dir + sub_path + "/" + board_name
                print("Compiling for:", sub_path, ", board:", board_name)
                os.makedirs(project_out_dir)

                compile_log_path = project_out_dir + "/" + "compile.log"
                execute_compile(arduino_cli, board_fqbn, project_path, project_out_dir, compile_log_path)
                ret = analysys_log(project_out_dir, compile_log_path)
                if ret == False:
                    print("===> Atention... Compiled error: " + str(project_path), "\n")
                    status_build.append(False)
                else:
                    status_build.append(True)

    # Generate compile report
    generate_html(out_root_dir, sub_path_list, board_name_list, status_build)                

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run compilation.', epilog="Example: ./arduino_cli.py --arduino_cli /home/tools/arduno-cli --arduino_lib /home/arduino --projects ezble --board xg24explorerkit")
    parser.add_argument('--arduino_cli', action='store', help="Path of arduino_cli tool.")
    parser.add_argument('--arduino_lib', action='store', help="Path of arduino library.")
    parser.add_argument("--projects", action='store', default='all', help="Choose projects to build, set: 'all' or ignore to build all projects.")
    parser.add_argument("--board", type=str, default='all', help="Choose board, set: 'all' or ignore to build all board variants.")

    args = parser.parse_args()
    
    if args.arduino_cli == None:
        print("Please set arduino cli tool path")
        sys.exit(1)
    
    if args.arduino_lib == None:
        print("Please set arduino library path")
        sys.exit(1)

    # get current dir and create output dir
    cur_dir = os.getcwd()
    # create out dir
    for i in range(0, 10):
        out_name = "output_" + str(i)
        out_root_dir = os.path.join(cur_dir, out_name)
        if os.path.isdir(out_root_dir) == False:
            os.mkdir(out_root_dir)
            break

    ezBLE_app_dir = os.path.join(args.arduino_lib, "libraries/ezBLE/examples")
    Matter_app_dir = os.path.join(args.arduino_lib, "libraries/Matter/examples")
    SiliconLabs_app_dir = os.path.join(args.arduino_lib, "libraries/SiliconLabs/examples")
    Builtin_app_dir = os.path.join(args.arduino_lib, "libraries/Builtin/examples")

    # #### Check project
    if (args.projects).lower() == "all":
        example_root_dir_list = [ezBLE_app_dir, Matter_app_dir, SiliconLabs_app_dir, Builtin_app_dir]
    elif (args.projects).lower() == "ezble":
        example_root_dir_list = [ezBLE_app_dir]
    elif (args.projects).lower() == "matter":
        example_root_dir_list = [Matter_app_dir]
    # SiliconLabs_app_dir
    elif (args.projects).lower() == "ble":
        example_root_dir_list = [SiliconLabs_app_dir]
    elif (args.projects).lower() == "builtin":
        example_root_dir_list = [Builtin_app_dir]        
    else:
        print("===> You choosed default mode - will build for all projects.\n")    

    #### Check board
    if (args.board).lower() == "all":
        print("===> You choosed default mode - will build for all variants.\n")

    compile_project(args.arduino_cli, example_root_dir_list, args.board, out_root_dir)
