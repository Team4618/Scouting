package team4618.scoutingapp.client.Views;

import android.content.Context;
import android.text.InputFilter;
import android.text.InputType;
import android.view.Gravity;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

public class strInput extends LinearLayout implements QuestionView {

    TextView question;
    EditText input;
    String JSONLabel;

    public strInput(Context context, String question, int maxChars, String JSONLabel) {
        super(context);
        this.JSONLabel = JSONLabel;

        //setup layout
        setOrientation(LinearLayout.VERTICAL);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        params.gravity = Gravity.CENTER_HORIZONTAL;
        setLayoutParams(params);

        //setup question text
        this.question = new TextView(context);
        this.question.setText(question);
        this.question.setTextAlignment(TEXT_ALIGNMENT_CENTER);
        addView(this.question);


        //setup EditText (str input)
        input = new EditText(context);
        input.setLayoutParams(new LinearLayout.LayoutParams(LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        input.setInputType(InputType.TYPE_TEXT_FLAG_MULTI_LINE);

        if(maxChars > 0) {
            //set max chars
            InputFilter[] filter = new InputFilter[1];
            filter[0] = new InputFilter.LengthFilter(maxChars);
            input.setFilters(filter);
        }

        addView(input);
    }

    public String getValue() {
        return input.getText().toString();
    }

    public String getJSONLabel() {
        return JSONLabel;
    }

    @Override
    public void resetValues() {
        input.setText(null);
    }
}
