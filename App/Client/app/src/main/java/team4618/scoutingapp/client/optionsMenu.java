package team4618.scoutingapp.client;

import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.net.Uri;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONException;

import java.io.*;
import java.util.ArrayList;

public class optionsMenu extends AppCompatActivity {
    ArrayAdapter listAA;
    ArrayList<String> MACsAL;
    View selectedView;
    int selectedViewPosition;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_options_menu);

        setTitle("Options");

        ListView list = findViewById(R.id.MAC);
        MACsAL = new ArrayList<>();
        for (int i = 0; i < MainActivity.MACs.length(); i++) {
            try {
                MACsAL.add((String) MainActivity.MACs.get(i));
            } catch (JSONException ex) {
                ex.printStackTrace();
            }
        }
        listAA = new ArrayAdapter<>(this, R.layout.remove_mac, MACsAL);
        list.setAdapter(listAA);

        list.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                if (selectedView != null) {
                    selectedView.setBackgroundColor(Color.WHITE);
                }
                selectedView = view;
                selectedViewPosition = i;
                view.setBackgroundColor(Color.parseColor("#257AFD"));
            }
        });
    }

    public void addAddress(View view) {
        try { //taken from https://stackoverflow.com/questions/8831050/android-how-to-read-qr-code-in-my-application

            Intent intent = new Intent("com.google.zxing.client.android.SCAN");
            intent.putExtra("SCAN_MODE", "QR_CODE_MODE"); // "PRODUCT_MODE for bar codes

            startActivityForResult(intent, 0);

        } catch (Exception e) {

            Uri marketUri = Uri.parse("market://details?id=com.google.zxing.client.android");
            Intent marketIntent = new Intent(Intent.ACTION_VIEW,marketUri);
            startActivity(marketIntent);

        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == 0) {

            if (resultCode == RESULT_OK) {
                String address = data.getStringExtra("SCAN_RESULT").toUpperCase();

                if (address.split("-").length == 6) {
                    address = address.replace('-', ':');
                }
                MACsAL.add(address);
                MainActivity.MACs.put(address);
                listAA.notifyDataSetChanged();

                writeJson();
            }
        }
    }

    public void removeAddress(View view) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if (!listAA.isEmpty()) {
                    String address = ((TextView) selectedView).getText().toString();
                    MACsAL.remove(selectedViewPosition);
                    MainActivity.MACs.remove(selectedViewPosition);
                    listAA.notifyDataSetChanged();

                    writeJson();

                    Toast.makeText(getApplicationContext(), "Removed the address " + address +
                            " from the whitelist", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    void writeJson() {
        File f = new File(getFilesDir(), "MAC.json");
        try (PrintWriter out = new PrintWriter(f)){
            out.println(MainActivity.MACs.toString());
        } catch (FileNotFoundException ex) {
            ex.printStackTrace();
        }
    }

    @Override
    public void onBackPressed() {
        startActivity(new Intent(this, MainActivity.class));
        super.onBackPressed();
    }
}
