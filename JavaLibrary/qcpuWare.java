package qcpuWare.jar;

import java.io.IOException;
import java.net.URL;
import java.util.Scanner;

//so what we need to get from the server (and have the java code generate) is the domain array, the equation, and the min/max boolean
public class qcpuWare{

    public static String serverIP; //this variable stores the server's ip address
    public static String serverPw = "QCPU";

    //these funtions are called by the user, and each specify the type of problem that will be sent to the server
    //###########################################################################################################//

    public static String ModeSet(String mode){ //function to set the mode of the qcpu

        String out = "";

        if (mode == "funcExtreme"){
            //if the function extreme solver mode is selected
            out = "funcExtreme";
        }

        else if (mode == "BCSP"){
            //if the binary constraint satisfaction problem solver mode is selected
            out = "BCSP";
        }

        else{
            System.out.println("Invalid qcpu mode selected: " + mode);
        }

        out = out + "%0A";
        return (out);

    }

    public static String DomainSet(double[] domain){ //function that sends the domain array to the qcpu

        //make the array into a string to send to webserver
        String arryStr = "[";
        for (int i = 0; i < domain.length-1; i++){
            arryStr += Double.toString(domain[i]) + ", ";
        }
        arryStr += domain[domain.length-1] + "]%0A";

        //return this string of our array
        return arryStr;

    }

    public static String FunctionSet(String eq, boolean max){ //function that sends the function to be solved to the qcpu
        //combine string of eq and the boolean to maximise or minimise:
        String eqStr = eq + "%0A";

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

    public static String ConstSet(String[] constraints, int numOfVars){ //function to convert array of constraints into a single string to be sent to qcpu

        String out = "";

        for (int i = 0; i < (constraints.length - 1); i++){
            out += constraints[i] + ";";
        }

        //add final entry without the semicolon
        out += constraints[constraints.length-1];

        out += "%0A" + Integer.toString(numOfVars); //add number of binary variables to server input

        return (out);

    }

    //this function gets the result from the server, and returns it
    //#############################################################//

    public static double[] SendToQCPU(String data) {//function to send information as a string to the server running on the qcpu
        try {
            //format the data:
            data = serverPw + data;
            data = Format(data);

            //this variable is the ip addr of the server:
            String ip = serverIP;

            //clear the results file
            System.out.println("http://" + ip + "/storage.php?input=" + data);
            ClrRes();
            //send string to server
            String send = new Scanner(new URL("http://" + ip + "/storage.php?input=" + data).openStream(), "UTF-8").useDelimiter("\\A").next();

            System.out.println("Printed...\n" + send);

            //now we get the result from the server

            while (!ReadyToRead(ip)) { //while the result isn't ready
                try {
                    Thread.sleep(10); //sleep for 1/100th of a second
                } catch (Exception e) {
                }
            }

            //if we have gotten to this point, we can now read the results
            String arrayResult = ReadServer(ip);

            double[] output;

            output = StringToArray(arrayResult);

            return output;

        }
        catch (IOException e){ //connection error
            System.out.println("QCPU-Ware has encountered an exception:\n" + e + "\nError connecting to server, check ip address and password, and that the server is turned on");
            return null;
        }

    }

    //these functions are all used to manipulate the data being sent to, and returning from the server
    //################################################################################################//

    private static void ClrRes() throws IOException {
        String clear = new Scanner(new URL("http://" + serverIP + "/storage.php?clrRes=True").openStream(), "UTF-8").useDelimiter("\\A").next();
    }

    private static String Format(String input){ //this function formats the input properly to be inserted into a url
        String[] revised = input.split(" ");
        String output = "";
        for (int i = 0; i < revised.length; i++){
            output = output + revised[i] + "%20";
        }

        output = output.replace("+", "%2B");
        return output;
    }

    public static void SetQcpuIP(String ip){ //this function sets the value of the ip variable, which the user specifies in their code
        serverIP = ip;
    }

    public static void SetQcpuPw(String pw){
        serverPw = pw;
    }

    private static String ReadServer(String ip) throws IOException { //function to get the output of the server:
        String output = new Scanner(new URL("http://" + ip + "/results.txt").openStream(), "UTF-8").useDelimiter("\\A").next();

        return output;

    }

    private static boolean ReadyToRead(String ip) throws IOException{ //function to check if the result file has been updated, and is ready to be read from
        String check = ReadServer(ip);
        if((check.split(" ")).length < 2){ //the result isn't ready
            return false;
        }
        else{ //the result is ready
            return true;
        }

    }

    private static double[] StringToArray(String input){ //this function converts the input string of an array into a double[] array
        String[] inputSplit = input.split(", ");
        inputSplit[(inputSplit.length)-1] = inputSplit[(inputSplit.length)-1].replace("]", ""); //reformat first and last entry
        inputSplit[0] = inputSplit[0].replace("[", "");
        //loop over the String array and convert it into a double[]
        double[] output = new double[inputSplit.length];
        for (int i = 0; i < inputSplit.length; i++){
            output[i] = Double.valueOf(inputSplit[i]);
        }

        return output;
    }

}
