package team4618.scoutingapp.client.Views;

import android.content.Context;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class tallyInt extends LinearLayout implements QuestionView {

    int count;
    TextView countTxt;
    TextView question;
    LinearLayout llHorizontal;
    String JSONLabel;

    public tallyInt(Context context, String question, String JSONLabel) {
        super(context);
        this.JSONLabel = JSONLabel;

        //setup the (linear)layout
        setOrientation(LinearLayout.VERTICAL);

        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        params.gravity = Gravity.CENTER_HORIZONTAL;
        setLayoutParams(params);

        //setup question
        this.question = new TextView(context);
        this.question.setText(question);
        this.question.setTextAlignment(TEXT_ALIGNMENT_CENTER);

        addView(this.question);

        //setup second LinearLayout
        llHorizontal = new LinearLayout(context);
        LinearLayout.LayoutParams paramsH = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        paramsH.gravity = Gravity.CENTER_HORIZONTAL;
        llHorizontal.setLayoutParams(paramsH);

        //setup text that displays count
        countTxt = new TextView(context);
        countTxt.setText("0");
        countTxt.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        llHorizontal.addView(countTxt);

        //setup plus and minus buttons
        Button plus = new Button(context);
        plus.setText("+");
        plus.setOnClickListener(new Button.OnClickListener() {
            public void onClick(View v) {
                count++;
                countTxt.setText(Integer.toString(count));
            }
        });
        plus.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        llHorizontal.addView(plus);

        Button minus = new Button(context);
        minus.setText("-");
        minus.setOnClickListener(new Button.OnClickListener() {
            public void onClick(View v) {
                if (count > 0) {
                    count--;
                    countTxt.setText(Integer.toString(count));
                }
            }
        });
        minus.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        llHorizontal.addView(minus);

        addView(llHorizontal);
    }

    public Integer getValue() {
        return count;
    }

    public String getJSONLabel() {
        return JSONLabel;
    }

    @Override
    public void resetValues() {
        count = 0;
        countTxt.setText("0");
    }
}
