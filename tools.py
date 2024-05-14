import os
import sys
import dload
import tarfile
import stat

tools_folder_path = "opt"

# Install Java17
def install_java():
	java_url = "https://artifactory.silabs.net/artifactory/studio-generic-production/java17/java17_linux_x86_64.zip"
	java_binary_path = os.path.join(tools_folder_path, "java17_linux_x86_64/jre/bin/java")
	if not os.path.isfile(java_binary_path):
		print("Downloading and unzipping java17 ...")
		dload.save_unzip(java_url, tools_folder_path, delete_after=True)
	
		# Give execute permission
		st = os.stat(java_binary_path)
		os.chmod(java_binary_path, st.st_mode | stat.S_IEXEC)
	else:
		print("java17 already installed")

# Install Sli-cli tool
def install_sli_cli():
	slc_cli_url = "https://www.silabs.com/documents/login/software/slc_cli_linux.zip"
	
	if not os.path.isfile(os.path.join(tools_folder_path, "slc_cli/slc")):
		print("Downloading and unzipping slc_cli ...")
		dload.save_unzip(slc_cli_url, tools_folder_path, delete_after=True)
		
		# Give execute permissions for slc-cli binary
		st = os.stat(os.path.join(tools_folder_path, "slc_cli", "slc"))
		os.chmod(os.path.join(tools_folder_path,"slc_cli", "slc"), st.st_mode | stat.S_IEXEC) 
	else:
		print("slc_cli already installed")

# Install Sim5
def install_sim5():
	sim5_url = "https://github.com/silabs-CongD/tools/releases/download/v2.0/SimplicityStudio-5_linux.tgz"
	sim5_path = os.path.join(tools_folder_path, "SimplicityStudio_v5")
	if not os.path.isfile(os.path.join(sim5_path, "studio")):
		print("Downloading and unzipping Sim5 ...")
		dload.save(sim5_url, os.path.join(tools_folder_path, "ss.tar.gz"))
		tar = tarfile.open(os.path.join(tools_folder_path,"ss.tar.gz"), "r:gz")
		tar.extractall(path=tools_folder_path)
		tar.close()
		os.remove("ss.tar.gz")
	else:
		print("Sim5 already installed")

# Install gcc_12.2
def install_gcc_12():
	arm_toolchain_url = "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.rel1/binrel/arm-gnu-toolchain-12.2.rel1-x86_64-arm-none-eabi.tar.xz?rev=7bd049b7a3034e64885fa1a71c12f91d&hash=732D909FA8F68C0E1D0D17D08E057619"
	
	arm_gcc_dir = os.path.join(tools_folder_path, "arm-gnu-toolchain-12.2.rel1-x86_64-arm-none-eabi")
	arm_toolchain_path = os.path.join(arm_gcc_dir, "bin")
	if not os.path.isfile(os.path.join(arm_toolchain_path, "arm-none-eabi-gcc")):
		print("Downloading and unzipping arm-none-eabi-gcc ...")
		dload.save(arm_toolchain_url, os.path.join(tools_folder_path, "gcc.tar.xz"))
		tar = tarfile.open(os.path.join(tools_folder_path, "gcc.tar.xz"), "r:xz")  
		tar.extractall(path=tools_folder_path)
		tar.close()
		# os.remove("gcc.tar.xz")
	else:
		print("gcc12.2 already installed")

##############################################
install_java()
install_sli_cli()
install_sim5()
install_gcc_12()
