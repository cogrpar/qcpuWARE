class setup{
  public static void main (String [] args){
    //this is the instalation code for the java library (execute as root)

    //else if args[0] is update
    if(args[0].contains("update")){
      //git pull
      System.out.println("updating...");
      try{
        Runtime.getRuntime().exec("git reset --hard && git pull");
      }catch(Exception e){}
    }
    
    //else
    else{
      System.out.println("Invalid arg: " + args[0]);
    }
    
  }
}
