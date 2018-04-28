package team4618.scoutingapp.client;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.os.Environment;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.text.format.Formatter;
import android.view.View;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.*;
import java.net.Inet4Address;
import java.net.Socket;
import java.util.ArrayList;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {
    static final int port = 4618;
    static Socket mainSocket;

    BluetoothSocket serverBTSocket;
    static ArrayList<String> MACs = new ArrayList<>();
    static final UUID uuid = UUID.fromString("cb3bd26c-4436-11e8-842f-0ed5f89f718b");

    static final String verification = "4618 SCOUTING APP";
    static InputStream in;
    static OutputStream out;
    static Boolean connected;


    static int requestPermsCode;
    static int[] grantResults;
    static Boolean canWrite = false;

    enum networkingType {
        hotSpot,
        BT,
        none
    }

    static networkingType netType;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        netType = networkingType.BT; //default

        setContentView(R.layout.activity_select_mode);
        setTitle("Select Networking Mode");

        //update MAC adress whitelist
        MACs.clear();
        MACs.add("08:D4:0C:E8:AA:43");

        if (new File(getFilesDir(), "MAC.txt").exists()) {
            try {
                FileInputStream fis = openFileInput("MAC.txt");

                byte[] buffer = new byte[1024];

                while (fis.read(buffer) != -1) {
                    for (String i : new String(buffer).trim().split("\\r?\\n")) {
                        MACs.add(i);
                    }
                }

                fis.close();

            } catch (FileNotFoundException ex) {
                ex.printStackTrace();
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        }
        canWrite = ContextCompat.checkSelfPermission(this, Manifest.permission.
                WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED; //check if we can write

        if (!canWrite)
            //request write perms if we don't have them, onRequestPermissionsResult is called when user
            //selects yes or no
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.
                    WRITE_EXTERNAL_STORAGE}, requestPermsCode);

    }

    public void selectModeHotSpot(View view) {
        netType = networkingType.hotSpot;
        goToMain();
    }

    public void selectModeBT(View view) {
        netType = networkingType.BT;
        goToMain();
    }

    public void selectModeNone(View view) {
        netType = networkingType.none;
        goToMain();
    }

    public void btnOptions(View view) {
        startActivity(new Intent(this, optionsMenu.class));
    }

    void goToMain() {
        setContentView(R.layout.activity_main);
        setTitle("Scouting");

        connected = false;
        new Thread(new Runnable() {
            @Override
            public void run() {
                connect();
            }
        }).start();
    }

    public void tallyUp(View view) {
        TextView text = (TextView) ((LinearLayout) view.getParent()).getChildAt(0);
        int tally = Integer.parseInt(text.getText().toString());
        tally++;
        text.setText(Integer.toString(tally));
    }

    public void tallyDown(View view) {
        TextView text = (TextView) ((LinearLayout) view.getParent()).getChildAt(0);
        int tally = Integer.parseInt(text.getText().toString());
        if (tally > 0)
            tally--;
        text.setText(Integer.toString(tally));
    }

    public void connect() {
        if (netType == networkingType.none) {
            canWrite = ContextCompat.checkSelfPermission(this, Manifest.permission.
                    WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED;
            if (!canWrite) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        setContentView(R.layout.activity_select_mode);
                        setTitle("Select Networking Mode");
                        Toast.makeText(getApplicationContext(), "Please enable write access and " +
                                "then try again.", Toast.LENGTH_SHORT).show();
                    }
                });
            }
            connected = true;
            return;
        } else if (netType == networkingType.hotSpot) {
            //get ip
            WifiManager wifi = (WifiManager) getApplicationContext().getSystemService(WIFI_SERVICE);
            String ip = Formatter.formatIpAddress(wifi.getConnectionInfo().getIpAddress());

            String serverIP = ip.substring(0, ip.lastIndexOf('.') + 1);
            serverIP += '1';

            try {
                System.out.println("trying to connect");
                mainSocket = new Socket(Inet4Address.getByName(serverIP), port);
                System.out.println("connected");
                out = mainSocket.getOutputStream();
                in = mainSocket.getInputStream();
            } catch (IOException ex) {
                ex.printStackTrace();
                return;
            }
        } else if (netType == networkingType.BT) {
            BluetoothAdapter btAdapter = ((BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE)).getAdapter();

            if (btAdapter == null || !btAdapter.isEnabled()) {
                int enableBtRequest = 0;
                Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
                startActivityForResult(enableBtIntent, enableBtRequest);
            }

            BluetoothDevice server = null;
            for (BluetoothDevice i : btAdapter.getBondedDevices()) {
                if (MACs.contains(i.getAddress())) {
                    server = i;
                }
            }

            if (server == null) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        Toast.makeText(getApplicationContext(), "Unable to find the server. Please make" +
                                " sure you are paired and then try again.", Toast.LENGTH_SHORT).show();
                    }
                });
                return;
            }

            try {
                serverBTSocket = server.createRfcommSocketToServiceRecord(uuid);
                serverBTSocket.connect();

                out = serverBTSocket.getOutputStream();
                in = serverBTSocket.getInputStream();
            } catch (IOException ex) {
                ex.printStackTrace();
                return;
            }

        }

        try {
            out.write(verification.getBytes());
            long end = System.currentTimeMillis() + 3000;
            while (System.currentTimeMillis() < end) {
                byte[] buffer = new byte[1024];
                int read = in.read(buffer);

                if (read == -1) { //we'll try again when we submit
                    System.out.println("Closed connection");
                    connected = false;
                    return;
                } else if (read > 0) {
                    String strRead = new String(buffer).trim();

                    if (!strRead.equals(verification)) {
                        //we'll try again when we submit
                        if (netType == networkingType.hotSpot) {
                            mainSocket.close();
                        } else if (netType == networkingType.BT) {
                            serverBTSocket.close();
                        }
                    }

                    //we've sucessfully verified and connected
                    System.out.println("verified");
                    connected = true;
                }
            }
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }

    public void submit(View view) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                submitNetowrking();
            }
        }).start();
    }

    void submitNetowrking() {
        if (!connected) { //try to connect again
            connect();
        }
        if (!connected) { //still aren't connected
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Toast.makeText(getApplicationContext(), "We aren't able to connect. Please make sure " +
                            "you are connected to the server and then try again.", Toast.LENGTH_SHORT).show();
                }
            });
            return;
        }

        //get data from elements and make it into JSON
        JSONObject obj = getDataAsJSON();

        if (obj == null)
            return;

        try {
            String match = obj.get("match").toString();
            if (netType == networkingType.none) {
                //check if external storage is mounted and writable
                if (!Environment.MEDIA_MOUNTED.equals(Environment.getExternalStorageState())) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            Toast.makeText(getApplicationContext(), "We aren't able to write to " +
                                    "external storage. Please make sure it is mounted and not readonly and" +
                                    " then try again.", Toast.LENGTH_SHORT).show();
                        }
                    });
                } else {
                    //Read from file if it exists, otherwise make it
                    File f = new File(Environment.getExternalStoragePublicDirectory(Environment.
                            DIRECTORY_DOCUMENTS), "Scouting Files/" + match + ".json");
                    f.getParentFile().mkdirs();

                    JSONArray matchArray;
                    if (f.exists()) {
                        FileInputStream fis = new FileInputStream(f.getAbsolutePath());
                        StringBuffer matchFileContent = new StringBuffer();

                        byte[] buffer = new byte[1024];
                        int n;
                        while ((n = fis.read(buffer)) != -1) {
                            matchFileContent.append(new String(buffer, 0, n));
                        }
                        fis.close();

                        System.out.println(matchFileContent);

                        try {
                            matchArray = new JSONArray(matchFileContent);
                        } catch (JSONException ex) {
                            //file isn't JSON formatted, ignore it
                            matchArray = new JSONArray();
                        }
                    } else {
                        f.createNewFile();
                        matchArray = new JSONArray();
                    }

                    matchArray.put(obj);

                    FileOutputStream fos = new FileOutputStream(f.getAbsolutePath());
                    fos.write(obj.toString().getBytes());
                    fos.close();
                }
            } else {
                //make object into string and send it on its way
                System.out.println("sending");
                out.write(obj.toString().getBytes());
            }
        } catch (JSONException ex) {
            ex.printStackTrace();
        } catch (IOException ex) {
            ex.printStackTrace();
            if (netType != networkingType.none)
                connected = false;
        }
    }

    JSONObject getDataAsJSON() {
        JSONObject obj = new JSONObject();

        final ArrayList<View> invalidViews = new ArrayList<>();

        try {

            //this is gonna be fun
            //this should be done in a for loop but i would proabably have to write custom views and i don't want to
            //TODO: write custom views and put this stuff in a for loop
            switch (((RadioGroup) findViewById(R.id.rdoSide)).getCheckedRadioButtonId()) { //get the data for the side we start on
                case R.id.btnLeft:
                    obj.put("startingSide", "left");
                    break;
                case R.id.btnCentre:
                    obj.put("startingSide", "centre");
                    break;
                case R.id.btnRight:
                    obj.put("startingSide", "right");
                    break;
                case -1: //nothing is checked
                    invalidViews.add(findViewById(R.id.btnLeft));
                    invalidViews.add(findViewById(R.id.btnCentre));
                    invalidViews.add(findViewById(R.id.btnRight));
                    break;
                default:
                    break;
            }

            String toPut;
            obj.put("crossAutoLine", ((CheckBox) findViewById(R.id.chckCrossAutoLine)).isChecked());

            toPut = ((TextView) findViewById(R.id.countTxtAutoSwitch)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.countTxtAutoSwitch));
            else
                obj.put("autoCubesSwitch", Integer.parseInt(toPut));

            toPut = ((TextView) findViewById(R.id.countTxtAutoScale)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.countTxtAutoScale));
            else
                obj.put("autoCubesScale", Integer.parseInt(toPut));

            toPut = ((TextView) findViewById(R.id.countTxtAutoVault)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.countTxtAutoVault));
            else
                obj.put("autoCubesVault", Integer.parseInt(toPut));

            toPut = ((TextView) findViewById(R.id.countTxtTeleopScale)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.countTxtTeleopScale));
            else
                obj.put("teleopCubesScale", Integer.parseInt(toPut));

            toPut = ((TextView) findViewById(R.id.countTxtTeleopSwitch)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.countTxtTeleopSwitch));
            else
                obj.put("teleopCubesSwitch", Integer.parseInt(toPut));

            toPut = ((TextView) findViewById(R.id.countTxtTeleopVault)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.countTxtAutoVault));
            else
                obj.put("teleopCubesVault", Integer.parseInt(toPut));

            toPut = ((TextView) findViewById(R.id.countTxtDropedCubes)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.countTxtDropedCubes));
            else
                obj.put("droppedCubes", Integer.parseInt(toPut));

            toPut = ((TextView) findViewById(R.id.countTxtDefenseCubes)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.countTxtDefenseCubes));
            else
                obj.put("defenseCubes", Integer.parseInt(toPut));

            obj.put("attemptedClimb", ((CheckBox) findViewById(R.id.chckClimbAttempt)).isChecked());

            obj.put("helpedClimb", ((CheckBox) findViewById(R.id.chckHelpClimb)).isChecked());

            obj.put("climbed", ((CheckBox) findViewById(R.id.chckSucessfulyClimb)).isChecked());

            toPut = ((TextView) findViewById(R.id.rateScaleNumber)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.rateScaleNumber));
            else
                obj.put("rateScale", Integer.parseInt(toPut));

            toPut = ((TextView) findViewById(R.id.rateSwitchNumber)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.rateSwitchNumber));
            else
                obj.put("rateSwitch", Integer.parseInt(toPut));

            toPut = ((TextView) findViewById(R.id.rateOverallNumber)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.rateOverallNumber));
            else
                obj.put("rateBot", Integer.parseInt(toPut));

            toPut = ((TextView) findViewById(R.id.matchRobot)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.matchRobot));
            else
                obj.put("robot", Integer.parseInt(toPut));

            toPut = ((TextView) findViewById(R.id.matchNumber)).getText().toString();
            if (toPut.equals(""))
                invalidViews.add(findViewById(R.id.matchNumber));
            else
                obj.put("match", Integer.parseInt(((EditText) findViewById(R.id.matchNumber)).getText().toString()));

            obj.put("comments", ((EditText) findViewById(R.id.commentsEditTxt)).getText().toString());
        } catch (JSONException ex) {
            ex.printStackTrace();
        }

        if (invalidViews.size() > 0) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    for (View i : invalidViews) {
                        i.getBackground().setColorFilter(Color.RED, PorterDuff.Mode.DARKEN); //add a red background to invalid views
                        //this doesn't work for the radio buttons though
                    }

                    Toast.makeText(getApplicationContext(), "Some things weren't filled in. Please" +
                            " fill them in then try again", Toast.LENGTH_SHORT).show();
                }
            });
            return null;
        } else {
            //redraw the whole view to set everything to the default value
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    setContentView(R.layout.activity_main);
                }
            });
            return obj;
        }
    }

    @Override
    public void onBackPressed() {
        setContentView(R.layout.activity_select_mode);
        setTitle("Select Networking Mode");
        if (connected) {
            try {
                if (netType == networkingType.hotSpot) {
                    mainSocket.close();
                } else if (netType == networkingType.BT) {
                    serverBTSocket.close();
                }
            }catch (IOException ex) {
                ex.printStackTrace();
            }
        }
        //super.onBackPressed(); //this closes the app for some reason...?
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
        //this should be okay as the only permissions we're requesting is write
        canWrite = grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED;
    }
}
