package team4618.scoutingapp.client;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.*;

import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;

public class optionsMenu extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_options_menu);

        setTitle("Options");
    }

    public void gotoWhiteListMAC(View view) {
        findViewById(R.id.btnMACWhitelist).setVisibility(View.GONE);
        findViewById(R.id.btnRmvMAC).setVisibility(View.GONE);
        findViewById(R.id.btnAddWhteList).setVisibility(View.VISIBLE);
        findViewById(R.id.MACtxt).setVisibility(View.VISIBLE);
    }

    public void whiteListMAC(View view) {
        String MAC = ((EditText) findViewById(R.id.MACtxt)).getText().toString();

        if (MAC.split("-").length == 6) {
            MAC = MAC.replace('-', ':');
        }
        MainActivity.MACs.add(MAC);

        try {
            FileOutputStream fo = openFileOutput("MAC.txt", Context.MODE_APPEND);
            fo.write((MAC + System.lineSeparator()).getBytes());
            fo.close();
        } catch (FileNotFoundException ex) {
            ex.printStackTrace();
        } catch (IOException ex) {
            ex.printStackTrace();
        }

        ((EditText) findViewById(R.id.MACtxt)).getText().clear();
    }

    public void gotoRemoveMAC(View view) {
        findViewById(R.id.btnMACWhitelist).setVisibility(View.GONE);
        findViewById(R.id.btnRmvMAC).setVisibility(View.GONE);

        ListView list = findViewById(R.id.MAC);
        list.setVisibility(View.VISIBLE);

        final ArrayAdapter aa = new ArrayAdapter<>(this, R.layout.remove_mac, MainActivity.MACs);
        list.setAdapter(aa);

        list.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                final String MAC = ((TextView) view).getText().toString();
                final int j = i;

                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        MainActivity.MACs.remove(j);
                        aa.notifyDataSetChanged();
                        Toast.makeText(getApplicationContext(), "Removed the adress " + MAC +
                                " from the whitelist", Toast.LENGTH_SHORT).show();
                    }
                });
            }
        });
    }

    @Override
    public void onBackPressed() {
        startActivity(new Intent(this, MainActivity.class));
        super.onBackPressed();
    }
}
