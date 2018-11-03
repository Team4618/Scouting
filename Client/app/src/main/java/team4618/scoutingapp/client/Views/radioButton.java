package team4618.scoutingapp.client.Views;

import android.content.Context;
import android.view.Gravity;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;

import java.util.ArrayList;

public class radioButton extends LinearLayout implements QuestionView {
    //creates a field with a question and then a series of radiobuttons for the user to answer with

    TextView question;
    RadioGroup choicesrdoGp;
    ArrayList<RadioButton> choices;
    String JSONLabel;

    public radioButton(Context context) {
        super(context);
    }

    public radioButton(Context context, String question, String JSONLabel, String... choices) {
        super(context);
        this.JSONLabel = JSONLabel;

        //setup the (linear)layout
        setOrientation(LinearLayout.VERTICAL);

        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        params.gravity = Gravity.CENTER_HORIZONTAL;
        setLayoutParams(params);

        //setup question
        this.question = new TextView(context);
        this.question.setText(question);
        this.question.setTextAlignment(TEXT_ALIGNMENT_CENTER);

        addView(this.question);

        //setup the radioButtons
        choicesrdoGp = new RadioGroup(context);
        RadioGroup.LayoutParams rdoParams = new RadioGroup.LayoutParams(RadioGroup.LayoutParams.WRAP_CONTENT, RadioGroup.LayoutParams.WRAP_CONTENT);
        rdoParams.gravity = Gravity.CENTER_HORIZONTAL;
        choicesrdoGp.setLayoutParams(rdoParams);
        choicesrdoGp.setOrientation(RadioGroup.HORIZONTAL);

        this.choices = new ArrayList<>();

        for (String choice : choices) {
            RadioButton rdoBtn = new RadioButton(context);
            rdoBtn.setText(choice);
            rdoBtn.setLayoutParams(new RadioGroup.LayoutParams(RadioGroup.LayoutParams.WRAP_CONTENT, RadioGroup.LayoutParams.WRAP_CONTENT));

            choicesrdoGp.addView(rdoBtn);
            this.choices.add(rdoBtn);
        }

        addView(choicesrdoGp);
    }

    public String getValue() {
        String checked = "";

        for (RadioButton i : choices) {
            if (i.isChecked()) {
                checked = (String) i.getText();
                break;
            }
        }

        return checked.toLowerCase();
    }

    public String getJSONLabel() {
        return JSONLabel;
    }

    @Override
    public void resetValues() {
        choicesrdoGp.check(-1);
    }
}
