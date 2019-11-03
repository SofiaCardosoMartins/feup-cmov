package org.feup.cmov.acmecustomer.activities;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import org.feup.cmov.acmecustomer.R;
import org.feup.cmov.acmecustomer.models.Customer;
import org.feup.cmov.acmecustomer.models.PaymentInfo;
import org.feup.cmov.acmecustomer.services.Register;

public class RegisterActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        TextView login = findViewById(R.id.have_an_account);
        login.setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        changeToLoginScreen();
                    }
                }
        );

        Button submitButton = findViewById(R.id.submit_button);
        submitButton.setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        onFinishedRegistration();
                    }
                }
        );
    }

    protected void onFinishedRegistration() {
        String name = ((EditText)findViewById(R.id.input_name)).getText().toString();
        String username = ((EditText)findViewById(R.id.input_username)).getText().toString();
        String password = ((EditText)findViewById(R.id.input_password)).getText().toString();

        String cardNumber = ((EditText)findViewById(R.id.input_card_number)).getText().toString();
        String cardHolder = ((EditText)findViewById(R.id.input_card_holder)).getText().toString();
        int cardMonth = parseInt(((EditText)findViewById(R.id.input_card_expiration_month)).getText().toString());
        int cardYear = parseInt(((EditText)findViewById(R.id.input_card_expiration_year)).getText().toString());
        int cvv = parseInt(((EditText)findViewById(R.id.input_cvv)).getText().toString());

        if(noErrorsOnRegistration()) {
            TextView errorMessage = findViewById(R.id.error_message);
            errorMessage.setText("");
            errorMessage.setVisibility(View.GONE);

            Customer newCustomer = new Customer(name,
                    username,
                    password,
                    new PaymentInfo(cardNumber, cardHolder, cardMonth, cardYear, cvv));

            // Making register request to API
            new Thread(new Register(newCustomer)).start();
            System.out.println("Am I not getting here wtf");

            // Maybe use this https://www.codejava.net/java-core/concurrency/java-concurrency-executing-value-returning-tasks-with-callable-and-future
            // To know result of register and do something when it returns -> e.g. redirect to Main page


            Intent intent = new Intent(this, MainMenuActivity.class);
            intent.putExtra("Customer", newCustomer);
            startActivity(intent);
        } else {
            TextView errorMessage = findViewById(R.id.error_message);
            errorMessage.setText("Please verify the data before submit!");
            errorMessage.setVisibility(View.VISIBLE);
        }
    }

    protected void changeToLoginScreen() {
        Intent intent = new Intent(this, LoginActivity.class);
        startActivity(intent);
    }

    protected boolean noErrorsOnRegistration() {
        String name = ((EditText)findViewById(R.id.input_name)).getText().toString();
        String username = ((EditText)findViewById(R.id.input_username)).getText().toString();
        String password = ((EditText)findViewById(R.id.input_password)).getText().toString();
        String cardNumber = ((EditText)findViewById(R.id.input_card_number)).getText().toString();
        String cardHolder = ((EditText)findViewById(R.id.input_card_holder)).getText().toString();
        int cardMonth = parseInt(((EditText)findViewById(R.id.input_card_expiration_month)).getText().toString());

        return name.length() > 3 && username.length() > 3 && password.length() >= 5
                && cardNumber.length() == 16 && cardHolder.length() > 3
                && cardMonth > 0 && cardMonth <= 12;
    }

    private int parseInt(String s){
        if(s == null || s.isEmpty())
            return 0;
        else
            return Integer.parseInt(s);
    }

}
