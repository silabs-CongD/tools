def buildDocker(def par1, def par2) {
  println("build docker..." + par1)
}

def test(repo_name) {
  // def SONAR_PROJECT = REPO_NAME
  
  env.repo = repo_name
  println repo_name
  // println SONAR_PROJECT
  println env.repo
}

return this
