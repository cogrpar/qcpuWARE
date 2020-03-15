class setup{
  public static void main (String [] args){
    //this is the instalation code for the java library (execute as root)
    
    //if args[0] is install:
    if(args[0] == "install"){
      //execute command to add the software to classpath
      try{
        String workDir = System.getProperty("user.dir");
        Runtime.getRuntime().exec("javac -classpath .:" + workDir + " qcpuWare.java");
      }catch(Exception e){}
    }
    
    //else if args[0] is update
    else if(args[0] == "update"){
      //git pull
      try{
        Runtime.getRuntime().exec("git pull");
      }catch(Exception e){}
    }
    
    //else
    else{
      System.out.println("Invalid arg: " + arg[0]);
    }
    
  }
}
