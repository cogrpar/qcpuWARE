//package qcpuWare;

import java.io.IOException;
import java.net.URL;
import java.util.Scanner;

//so what we need to get from the server (and have the java code generate) is the domain array, the equation, and the min/max boolean
class qcpuWare{

  public String DomainSet(double[] domain){ //function that sends the domain array to the qcpu

    //make the array into a string to send to webserver 
    String arryStr = "["; 
    for (int i = 0; i < domain.length-1; i++){
      arryStr += Double.toString(domain[i]) + ", ";
    }  
    arryStr += domain[domain.length-1] + "]\n";

    //return this string of our array
    return arryStr;
     
  }

  public String FunctionSet(String eq, boolean max){ //function that sends the function to be solved to the qcpu
    //combine string of eq and the boolean to maximise or minimise:
    String eqStr = eq + "\n";

    if (max){
      //if max is true:
      eqStr += "True";
    }
    else{
      //if max is false
      eqStr += "False";
    }

    return eqStr;

  }

  public double[] SendToQCPU(String data) throws IOException {//function to send information as a string to the server running on the qcpu

    //format the data:
    data = Format(data);

    //this variable is the ip addr of the server:
    ip = GetQcpuIp();

    //send string to server
    String send = new Scanner(new URL("http://" + ip + "/storage.txt/get?input=" + data).openStream(), "UTF-8").useDelimiter("\\A").next();
        
    System.out.println("Printed...\n" + send);

    //now we get the result from the server

    while(!ReadyToRead(ip)){ //while the result isn't ready
      try{
        Thread.sleep(10); //sleep for 1/100th of a second
      }catch (Exception e){}
    }

    //if we have gotten to this point, we can now read the results
    String arrayResult = ReadServer(ip);


    double[] output = new double[0];

    output = StringToArray(arrayResult);
    
    output[0] = 0;
    output[1] = 0;
    output[2] = 0;
    output[3] = 0;

    return output;

  }

  private String Format(String input){ //this function formats the input properly to be inserted into a url
    String[] revised = input.split(" ");
    String output = "";
    for (int i = 0; i < revised.length; i++){
        output = output + revised[i] + "%20";
    }

    return output;
  }

  private String GetQcpuIp(){ //this function is used to get the server's ip addr, by reading it from a file

    String ip = "http://192.168.1.51"; //we normally get this from file
    return (ip);
  }

  private String ReadServer(String ip) throws IOException { //function to get the output of the server:
    Scanner scan = new Scanner();
    String output = scan(new URL("http://192.168.1.51/result").openStream(), "UTF-8").useDelimiter("\\A").next();
    scan.close();

    return output;

  }

  private boolean ReadyToRead(String ip){ //function to check if the result file has been updated, and is ready to be read from
    String check = ReadServer(ip);
    if(check == ""){ //the result isn't ready
      return false;
    }
    else{ //the result is ready
      return true;
    }

  }

  private double[] StringToArray(String input){
    //this function converts the input string of an array into a double[] array
    String[] inputSplit = input.split(", ");
    inputSplit[(inputSplit.length)-1] = inputSplit[(inputSplit.length)-1].replace("]", ""); //reformat first and last entry
    inputSplit[0] = inputSplit[0].replace("]", "");

    //loop over the String array and convert it into a double[]
    double[] output = new double[inputSplit.len];
    for (int i = 0; i < inputSplit.len; i++){
      output[i] = String.toDouble(inputSplit[i]);
    }

    return output;
  }

}
