
env.SLC_CLI_URL="https://github.com/silabs-CongD/tools/releases/download/v1.4/slc_cli_linux.zip"
env.SL_SLC_PATH="opt/slc_cli/slc"
env.SL_MAKE_PATH="/usr/bin/make"

env.SS_URL="https://github.com/silabs-CongD/tools/releases/download/v2.0/SimplicityStudio-5_linux.tgz"
env.SONAR_SCANNER_URL="https://github.com/SiliconLabs/application_examples_ci/releases/download/v1.0/sonar-scanner-cli-6.2.1.4610-linux-x64.zip"
env.ARM_GCC_DIR="${WORKSPACE}/opt/SimplicityStudio_v5/developer/toolchains/gnu_arm/arm-gnu-toolchain-12.2.rel1-x86_64-arm-none-eabi"
env.SL_STUDIO_BUILD_PATH="opt/SimplicityStudio_v5"
env.STUDIO_ADAPTER_PACK_PATH="opt/SimplicityStudio_v5/developer/adapter_packs"
env.POST_BUILD_EXE="${WORKSPACE}/opt/SimplicityStudio_v5/developer/adapter_packs/commander/commander"		

env.SL_WORKSPACE_PATH="${WORKSPACE}"
env.JENKINS_BUILD_URL="${BUILD_URL}"
env.CI_REPO_DIR="${WORKSPACE}/ci_repo"


def poll_the_change() {

  script {
    currentBuild.displayName = "PR#${ghprbPullId}: ${ghprbSourceBranch}"

      // Clone project
    withCredentials([gitUsernamePassword(credentialsId: 'github-username-token', gitToolName: 'Default')]) {
      sh 'git clone --branch $ghprbSourceBranch $ghprbAuthorRepoGitUrl projects'
    }
    sh '''
    mkdir poll_the_change
    cp -r projects poll_the_change

    cd poll_the_change/projects
    echo "${ghprbPullLongDescription}" > pr_description.txt
    bash $WORKSPACE/pull_request_process/scripts/check_changed_projects.sh pr_description.txt $ghprbActualCommit > check_changed_projects.txt
    
    '''

    tmp = readFile('poll_the_change/projects/check_changed_projects.txt').trim()
    if (tmp.contains("Skip check. PR bot is disabled.")) {
      currentBuild.description = "Skip check. PR bot is disabled."
      error("Skip check. PR bot is disabled.")
    }
    if (tmp.contains("Skip check. No changed project found.")) {
      currentBuild.description = "Skip check. No changed project found."
      error("Skip check. No changed project found.")
    }
    // Here we have some projects in pull request
    env.PROJECT_NAME = tmp

    // Check Bot auto commit
    dir('projects') {
      withCredentials([gitUsernamePassword(credentialsId: 'github-username-token', gitToolName: 'Default')]) {
        sh '''#!/bin/bash
        git log -1 --pretty=format:%s > $WORKSPACE/poll_the_change/check_bot_commit.log
        '''
      }
    }

    bot_commit = readFile('poll_the_change/check_bot_commit.log').trim()
    if (bot_commit.contains("Automatically update Shield for README.md")) {
      // Set this var to build .slcp only 1 board_id
      env.CHECK_SONARQUBE=1                           
    }                    
  }  
}

def install_tools_sw() {
  sh '''
  apt-get update -y
  apt-get install zip -y
  apt-get install make -y
  apt-get install p7zip-full -y
  pip3 install gitpython
  apt-get install git-lfs -y
  git lfs install --skip-repo
  
  curl -L -o slccli.zip \$SLC_CLI_URL
  unzip slccli.zip -d opt > /dev/null && rm slccli.zip
  chmod +x $SL_SLC_PATH

  curl -L -o ss.tgz \$SS_URL
  tar -xvf ss.tgz -C opt > /dev/null && rm ss.tgz
  chmod +x $WORKSPACE/opt/SimplicityStudio_v5/developer/toolchains/gnu_arm/10.3_2021.10

  curl -L -o 12.2.tgz "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.rel1/binrel/arm-gnu-toolchain-12.2.rel1-x86_64-arm-none-eabi.tar.xz?rev=7bd049b7a3034e64885fa1a71c12f91d&hash=2C60D7D4E432953DB65C4AA2E7129304F9CD05BF"
  tar -xvf 12.2.tgz -C opt/SimplicityStudio_v5/developer/toolchains/gnu_arm > /dev/null
  ls $SL_STUDIO_BUILD_PATH/developer/toolchains/gnu_arm
  chmod +x $ARM_GCC_DIR

  curl -L -o sonar_scanner.zip $SONAR_SCANNER_URL
  unzip sonar_scanner.zip -d opt > /dev/null
  chmod 777 $WORKSPACE/opt/sonar-scanner-6.2.1.4610-linux-x64/jre/bin/java
  '''
}

def clone_ci_repo() {
  dir('ci_repo') {
    git branch: 'master', 
    credentialsId: 'github-username-token', 
    url: 'https://github.com/SiliconLabs/application_examples_ci.git'
  }  
}

def install_zap_tool() {
  sh '''
  mkdir -p opt/zap
  curl -L -o zap-linux-x64.zip https://github.com/project-chip/zap/releases/download/v2024.11.01/zap-linux-x64.zip
  unzip zap-linux-x64.zip -d opt/zap > /dev/null && rm zap-linux-x64.zip
  $WORKSPACE/opt/zap/zap-cli status
  '''  
}

def add_bot_as_reviewer() {
  sh '''
  pwd
  mkdir bot_as_reviewer
  cd bot_as_reviewer

  # Get all requested reviewers for a pull request
  curl -H "Accept: application/vnd.github+json" -H "Authorization: token $AN_ACCESS_KEY_PSW" https://api.github.com/repos/${ghprbGhRepository}/pulls/${ghprbPullId}/requested_reviewers > requested_reviewers.json
  if grep -q "silabs-ci-bot" requested_reviewers.json; then
    echo "silabs-ci-bot is already reviewer for this pull request!"
  else
    echo "added silabs-ci-bot as reviewer for this pull request!"
    curl -X POST -H "Accept: application/vnd.github+json" -H "Authorization: token $AN_ACCESS_KEY_PSW" https://api.github.com/repos/${ghprbGhRepository}/pulls/${ghprbPullId}/requested_reviewers -d '{"reviewers":["silabs-ci-bot"]}'
  fi
  '''
}

def setBuildStatus(message, state, context, ref) {
	step([
		$class: "GitHubCommitStatusSetter",
		reposSource: [$class: "ManuallyEnteredRepositorySource", url: "${ghprbAuthorRepoGitUrl}"],
		commitShaSource: [$class: "ManuallyEnteredShaSource", sha: "${ghprbActualCommit}"],
		contextSource: [$class: "ManuallyEnteredCommitContextSource", context: context],
		errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
		statusBackrefSource: [$class: "ManuallyEnteredBackrefSource", backref: ref],
		statusResultSource: [$class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]]]
	]);
}

def check_pr_description() {
  sh '''
  pwd
  mkdir pr_description
  cd pr_description

  echo "${ghprbPullLongDescription}" > pr_description.txt
  bash $WORKSPACE/pull_request_process/scripts/check_pr_description.sh pr_description.txt > pr_description_report.html
  '''

  archiveArtifacts 'pr_description/pr_description_report.html'
  tmp = readFile('pr_description/pr_description_report.html')
  if (tmp.contains("FAILURE")) {
    setBuildStatus("Build failed", "FAILURE", "ci/build-CheckPullRequestDescription", "${BUILD_URL}/artifact/pr_description/pr_description_report.html");

    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
      sh "exit 1"
    }
  }
  else {
    setBuildStatus("Build succeeded", "SUCCESS", "ci/build-CheckPullRequestDescription", "${BUILD_URL}/artifact/pr_description/pr_description_report.html");
    sh 'exit 0'
  }  
}

def check_readme_file() {
  sh '''
  cd poll_the_change/projects
  bash $WORKSPACE/pull_request_process/scripts/check_readme_file_v2.sh $WORKSPACE/changed_projects.txt > readme_file_report.html
  '''

  archiveArtifacts 'poll_the_change/projects/readme_file_report.html'
  tmp = readFile('poll_the_change/projects/readme_file_report.html')
  if (tmp.contains("FAILURE")) {
    setBuildStatus("Build failed", "FAILURE", "ci/build-CheckReadmeFileStructure", "${BUILD_URL}/artifact/poll_the_change/projects/readme_file_report.html");

    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
      sh "exit 1"
    }
  } else {
    setBuildStatus("Build succeeded", "SUCCESS", "ci/build-CheckReadmeFileStructure", "${BUILD_URL}/artifact/poll_the_change/projects/readme_file_report.html");
    sh 'exit 0'
  }  
}

def check_coding_style() {
  sh '''
  mkdir coding_style
  cp -r projects coding_style
  cd coding_style/projects

  echo "$PROJECT_NAME" > changed_files.txt
  bash $WORKSPACE/pull_request_process/scripts/check_coding_style.sh changed_files.txt $BUILD_URL > coding_style_report.html
  '''

  archiveArtifacts 'coding_style/projects/coding_style_report.html'
  tmp = readFile('coding_style/projects/coding_style_report.html')
  if (tmp.contains("Some tests failed")) {
    archiveArtifacts 'coding_style/projects/uncrustify_formatted_files.zip, coding_style/projects/uncrustify_formatted_files/**/*.log'
    setBuildStatus("Build failed", "FAILURE", "ci/build-CheckCodingStyle", "${BUILD_URL}/artifact/coding_style/projects/coding_style_report.html");

    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
      sh 'exit 1'
    }
  } else { 
    setBuildStatus("Build succeeded", "SUCCESS", "ci/build-CheckCodingStyle", "${BUILD_URL}/artifact/coding_style/projects/coding_style_report.html");
    sh 'exit 0'
  }    
}

def check_build_report() {
  build_report = readFile('build_test_project.html')
	if (build_report.contains("Fail") | build_report.contains('FAIL')) {
		setBuildStatus("Build failed", "FAILURE", "ci/build-BuildTestProjects", "${BUILD_URL}/artifact/build_test_project.html");
		catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
			sh 'exit 1'
		}
	}
	else {
		setBuildStatus("Build succeeded", "SUCCESS", "ci/build-BuildTestProjects", "${BUILD_URL}/artifact/build_test_project.html");
		sh 'exit 0'
	}
}

def build_common_project() {
  env.repo = REPO_NAME

  sh '''
  export JAVA_HOME=$WORKSPACE/opt/sonar-scanner-6.2.1.4610-linux-x64/jre
  export PATH="usr/bin/python3:\$JAVA_HOME/bin:${PATH}"
  java --version
  $SL_SLC_PATH configuration -gcc $ARM_GCC_DIR
  
  mkdir changed_projects
  while read line; do cp -r ./projects/$line --parents ./changed_projects; done < changed_projects.txt

  export SCRIPT_PATH="$WORKSPACE/pull_request_process/scripts/checkproject.py"
  export PROJECT_PATH="changed_projects"
  python3 -u "$SCRIPT_PATH" --junit --html --release --slcpgcc --sls "$PROJECT_PATH"
  '''

  archiveArtifacts 'build_test_project.html'
  junit 'out/*.xml'
  
  check_build_report()    
}

return this
