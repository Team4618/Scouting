package team4618.scoutingapp.client;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothSocket;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.net.Uri;
import android.os.Bundle;
import android.os.Debug;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v4.content.FileProvider;
import android.support.v7.app.AppCompatActivity;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import team4618.scoutingapp.client.Views.*;

import java.io.*;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.UUID;

import static android.view.View.TEXT_ALIGNMENT_CENTER;

public class MainActivity extends AppCompatActivity {
    static final UUID uuid = UUID.fromString("cb3bd26c-4436-11e8-842f-0ed5f89f718b");
    static String verification = "4618 SCOUTING APP";
    static JSONArray MACs = new JSONArray();
    static InputStream in;
    static OutputStream out;
    static Boolean connected;
    static int requestPermsCode;
    static int[] grantResults;
    static Boolean canWrite = false;
    static networkingType netType;
    static String tag = "Scouting";
    BluetoothSocket serverBTSocket;
    ArrayList<QuestionView> questions;
    static int enableBTRequest = 0;
    static int imageCaptureRequest = 1;
    BluetoothDevice server = null;
    BluetoothAdapter btAdapter = null;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        netType = networkingType.BT; //default

        setContentView(R.layout.activity_select_mode);
        setTitle("Select Networking Mode");

        //set a text box that we can change verification with
        EditText verificationTV = findViewById(R.id.verification);
        verificationTV.addTextChangedListener(new TextWatcher() {
            //before and after text changed are left blank because idc about them, ontextchanged is what we want

            @Override
            public void beforeTextChanged(CharSequence charSequence, int i, int i1, int i2) {

            }

            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                verification = charSequence.toString();
                Log.d(tag, verification);
            }

            @Override
            public void afterTextChanged(Editable editable) {

            }
        });
        verificationTV.setText(verification);

        //update MAC address whitelist
        MACs = readJson();

        canWrite = ContextCompat.checkSelfPermission(this, Manifest.permission.
                WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED; //check if we can write

        if (!canWrite)
            //request write perms if we don't have them, onRequestPermissionsResult is called when user
            //selects yes or no
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.
                    WRITE_EXTERNAL_STORAGE}, requestPermsCode);
    }

    public JSONArray readJson() {
        //reads the JSON file containing our MAC addresses
        File MACFile = new File(getFilesDir(), "MAC.json");
        JSONArray jArray = new JSONArray();

        try {
            MACFile.createNewFile();
            InputStream is = new FileInputStream(MACFile);

            int size = is.available();
            byte[] buffer = new byte[size];

            is.read(buffer);
            is.close();

            String jArrayStr = new String(buffer, "UTF-8");

            if (jArrayStr.length() > 0) {
                jArray = new JSONArray(jArrayStr);
            }

        } catch (IOException ex) {
            ex.printStackTrace();
        } catch (JSONException ex) {
            ex.printStackTrace();
        }

        return jArray;
    }

    public void selectModeBT(View view) {
        netType = networkingType.BT;
        connected = false;
        new Thread(new Runnable() {
            @Override
            public void run() {
                connect();
            }
        }).start();
    }

    public void selectModeNone(View view) {
        netType = networkingType.none;
        connected = false;
        new Thread(new Runnable() {
            @Override
            public void run() {
                connect();
            }
        }).start();
    }

    public void selctModePit(View view) {
        setContentView(R.layout.activity_pit_scouting);
        setTitle("Pit Scouting");
    }

    public void takePicture(View view) {
        if (!getPackageManager().hasSystemFeature(PackageManager.FEATURE_CAMERA_ANY)) return;

        Intent takePicture = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        if (takePicture.resolveActivity(getPackageManager()) != null) {
            //get link to our documents folder, then our scouting
            File docs = Environment.getExternalStorageDirectory();
            File dir = new File(new File(docs, "pit scouting"), "img");

            //create our folder if it doesn't already exist
            if (!dir.exists()) {
                dir.mkdirs();
            }

            File imageFile = null;
            try {
                String teamNumber = ((EditText) findViewById(R.id.matchRobotPit)).getText().toString().substring(0, 4); //get team #
                imageFile = new File(dir, teamNumber + ".jpg");
                imageFile.createNewFile();
            } catch (IOException ex) {
                ex.printStackTrace();
            } catch (IllegalArgumentException ex) { //most likely team number isn't filled in
                ex.printStackTrace();
            } catch (StringIndexOutOfBoundsException ex) { //same as above
                ex.printStackTrace();
            }

            if (imageFile != null) {
                Uri photoUri = FileProvider.getUriForFile(this, "team4618.scoutingapp.client.fileprovider",
                        imageFile);

                takePicture.putExtra(MediaStore.EXTRA_OUTPUT, photoUri);
                startActivityForResult(takePicture, imageCaptureRequest);
            }
        }
    }

    public void submitPit(View view) {
        //this is where we would pull all our values from the pit layout, but honestly we're not going to use the data
        //so I don't really care
    }

    public void btnOptions(View view) {
        startActivity(new Intent(this, optionsMenu.class));
    }

    void goToMain() {
        setContentView(R.layout.activity_main);
        setTitle("Scouting");
    }

    void loadTemplate(final JSONArray template) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Context context = getApplicationContext();

                //create layout and set it up
                final LinearLayout ll = new LinearLayout(getApplicationContext());

                ll.setOrientation(LinearLayout.VERTICAL);
                LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.MATCH_PARENT);
                params.gravity = Gravity.CENTER_HORIZONTAL;
                ll.setLayoutParams(params);

                questions = new ArrayList<>();

                try {
                    for (int i = 0; i < template.length(); i++) {
                        JSONObject obj = template.getJSONObject(i);

                        switch (obj.getString("type")) {
                            default:
                                break;

                            case "header":
                                TextView header = new TextView(context);
                                header.setText(obj.getString("label"));
                                header.setTextSize(TypedValue.COMPLEX_UNIT_SP, 24);
                                header.setTextAlignment(TEXT_ALIGNMENT_CENTER);
                                header.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,
                                        LinearLayout.LayoutParams.WRAP_CONTENT));

                                ll.addView(header);
                                break;

                            case "space":
                                Space space = new Space(context);

                                //convert dps to pixels
                                float density = context.getResources().getDisplayMetrics().density;
                                int pixels = (int) (obj.getInt("size") * density + 0.5f);

                                space.setLayoutParams(new LinearLayout.LayoutParams(0, pixels));

                                ll.addView(space);
                                break;

                            case "rdoBtn":
                                //get the array of options
                                JSONArray options = obj.getJSONArray("options");
                                String[] optionsStr = new String[options.length()];

                                for (int j = 0; j < options.length(); j++) {
                                    optionsStr[j] = (String) options.get(j);
                                }

                                radioButton rb = new radioButton(context, obj.getString("question"), obj.getString("jsonLabel"), optionsStr);
                                ll.addView(rb);
                                questions.add(rb);
                                break;

                            case "chck":
                                checkbox chk = new checkbox(context, obj.getString("question"), obj.getString("jsonLabel"));
                                ll.addView(chk);
                                questions.add(chk);
                                break;

                            case "tallyInt":
                                tallyInt ti = new tallyInt(context, obj.getString("question"), obj.getString("jsonLabel"));
                                ll.addView(ti);
                                questions.add(ti);
                                break;

                            case "int":
                                intInput ii = new intInput(context, obj.getString("question"), obj.getInt("maxChars"), obj.getString("jsonLabel"));
                                ll.addView(ii);
                                questions.add(ii);
                                break;

                            case "str":
                                strInput si = new strInput(context, obj.getString("question"), obj.getInt("maxChars"), obj.getString("jsonLabel"));
                                ll.addView(si);
                                questions.add(si);
                                break;
                        }
                    }
                } catch (JSONException ex) {
                    ex.printStackTrace();
                }

                //add submit button
                final Button submit = new Button(context);
                submit.setText
                        ("Submit");
                submit.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        submit(null);
                    }
                });
                submit.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT));
                ll.addView(submit);

                goToMain();

                ScrollView questionsContainer = findViewById(R.id.questionsContainer);
                questionsContainer.addView(ll);
            }
        });
    }

    // Create a BroadcastReceiver for ACTION_FOUND.
    //https://developer.android.com/guide/topics/connectivity/bluetooth#java
    private final BroadcastReceiver mReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (BluetoothDevice.ACTION_FOUND.equals(action)) {
                System.out.println("we found a boi");

                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);

                for (int j = 0; j < MACs.length(); j++) {
                    try {
                        if (MACs.get(j).equals(device.getAddress())) {
                            server = device;
                            btAdapter.cancelDiscovery();
                        }
                    } catch (JSONException ex) {
                        ex.printStackTrace();
                    }
                }
            }
        }
    };

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

            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    setContentView(R.layout.activity_main_defualt);
                    setTitle("Scouting");
                }
            });
            return;

        } else if (netType == networkingType.BT) {
            btAdapter = ((BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE)).getAdapter();

            if (btAdapter == null || !btAdapter.isEnabled()) {
                Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
                startActivityForResult(enableBtIntent, enableBTRequest);
                return;
            }

            if (btAdapter.isDiscovering()) btAdapter.cancelDiscovery(); //we're already trying
            server = null;

            for (BluetoothDevice i : btAdapter.getBondedDevices()) {
                try {
                    for (int j = 0; j < MACs.length(); j++) {
                        if (MACs.get(j).equals(i.getAddress())) {
                            server = i;
                        }
                    }
                } catch (JSONException ex) {
                    ex.printStackTrace();
                }
            }

            if (server == null) {
                if (!btAdapter.isDiscovering()) {
                    System.out.println("scanning");
                    btAdapter.startDiscovery();
                }

                //https://developer.android.com/guide/topics/connectivity/bluetooth#java
                IntentFilter filter = new IntentFilter(BluetoothDevice.ACTION_FOUND);
                registerReceiver(mReceiver, filter);


                try {
                    Thread.sleep(2000);
                } catch (InterruptedException ex) {
                    ex.printStackTrace();
                }
                while (btAdapter.isDiscovering()) {
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
                Log.e(tag, "Caught error, making toast");

                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        Toast.makeText(getApplicationContext(), "Unable to connect to the server", Toast.LENGTH_SHORT).show();
                    }
                });
                return;
            }

        }

        try {
            out.write(verification.getBytes());
            out.flush();
            long end = System.currentTimeMillis() + 3000;
            while (System.currentTimeMillis() < end) {
                byte[] buffer;

                try {
                    buffer = new byte[1024];
                    int read = in.read(buffer);
                    if (read == -1) { //we'll try again when we submit
                        Log.d(tag, "Closed connection");
                        connected = false;
                        return;
                    }
                } catch (IOException ex) {
                    ex.printStackTrace();
                    return;
                }

                if (buffer.length > 0) {
                    String strRead = new String(buffer).trim();

                    if (!strRead.equals(verification)) {
                        //we'll try again when we submit
                        Log.d(tag, "Verification unsuccessful");
                        serverBTSocket.close();
                        return;
                    }

                    //we've sucessfully verified and connected
                    Log.d(tag, "verified");
                    connected = true;
                    break;
                }
            }

            if (connected) {
                boolean recived = false;
                String template = "";
                while (!recived) {

                    int len;
                    while (true) {
                        byte[] buffer = new byte[4];
                        int read = in.read(buffer);

                        if (read == -1) { //we'll try again when we submit
                            Log.d(tag, "Closed connection");
                            connected = false;
                            return;
                        } else if (read > 0) {
                            len = (ByteBuffer.wrap(buffer)).getInt();
                            break;
                        }
                    }


                    while (template.length() < len) {
                        byte[] buffer = new byte[1024];
                        int read = in.read(buffer);

                        if (read == -1) { //we'll try again when we submit
                            Log.d(tag, "Closed connection");
                            connected = false;
                            return;
                        } else if (read > 0) {
                            template += new String(buffer).replace("\0", "");
                        }
                    }

                    recived = true;
                    /*//make sure there's no corruption, check end and beginning
                    System.out.println(template);
                    if (template.startsWith("[{") && template.endsWith("}]")) {
                        recived = true;
                    }

                    //send if everything was recived properly
                    out.write((byte) (recived ? 'Y' : 'N'));
                    out.flush();*/
                }

                try {
                    loadTemplate(new JSONArray(template));
                } catch (JSONException ex) {
                    ex.printStackTrace();
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
                Log.d(tag, "sending");
                out.write(obj.toString().getBytes());
                out.flush();
            }
        } catch (JSONException ex) {
            ex.printStackTrace();
        } catch (IOException ex) {
            ex.printStackTrace();
            if (netType != networkingType.none)
                connected = false;
        }
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

    JSONObject getDataAsJSON() {
        JSONObject obj = new JSONObject();
        if (netType == networkingType.none) {

            final ArrayList<View> invalidViews = new ArrayList<>();

            try {

                //this is gonna be fun
                //this should be done in a for loop but i would proabably have to write custom views and i don't want to
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

                obj.put("brokeDown", ((CheckBox) findViewById(R.id.chckBreakDown)).isChecked());

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
            }
        } else {
            try {
                for (final QuestionView i : questions) {
                    obj.put(i.getJSONLabel(), i.getValue());

                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            i.resetValues();
                        }
                    });
                }
            } catch (JSONException ex) {
                ex.printStackTrace();
            }
        }

        return obj;
    }

    @Override
    public void onBackPressed() {
        if (connected && serverBTSocket != null) {
            try {
                serverBTSocket.close();
            } catch (IOException ex) {
                ex.printStackTrace();
            }

            connected = false;
        }

        setContentView(R.layout.activity_select_mode);
        setTitle("Select Networking Mode");
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
        if (requestCode == enableBTRequest) {
            canWrite = grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED;
        }

    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == imageCaptureRequest && resultCode == RESULT_OK) {
            Bitmap pictureThumb = (Bitmap) data.getExtras().get("data");

            ImageView imageView = findViewById(R.id.robotImagePit);
            imageView.setImageBitmap(pictureThumb);
            imageView.setVisibility(View.VISIBLE);
        }
    }

    enum networkingType {
        BT,
        none
    }
}