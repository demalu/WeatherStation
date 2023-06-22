package com.example.provaappweatherstation

import android.app.ProgressDialog
import android.content.Intent
import android.os.Bundle
import android.text.TextUtils
import android.util.Patterns
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.ActionBar
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.AppCompatButton
import com.google.firebase.FirebaseApp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.ktx.auth
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.ktx.Firebase

class SignUpActivity: AppCompatActivity() {
    private lateinit var auth: FirebaseAuth //al posto di "FirebaseAuth.getInstance()
    private lateinit var db : FirebaseFirestore

    //ActionBar
    private lateinit var actionBar: ActionBar

    //Progress Dialog
    private lateinit var progressDialog: ProgressDialog

    //user obj
    //private lateinit var data_user: Userdata
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.signup_activity)
        auth= Firebase.auth
        val login = findViewById<TextView>(R.id.sign_in_textView)
        login.setOnClickListener {
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
        }

        val signup_btn = findViewById<AppCompatButton>(R.id.sign_button)
        signup_btn.setOnClickListener{
            performSignup()
        }

    }

    private fun performSignup() {
        val name = findViewById<EditText>(R.id.nameUser_text)
        val email = findViewById<EditText>(R.id.email_text)
        val password = findViewById<EditText>(R.id.password_text)
        val inputname = name.text.toString()
        val inputemail = email.text.toString()
        val inputpassword = password.text.toString()

        if(name.text.isEmpty() || email.text.isEmpty() || password.text.isEmpty()){
            Toast.makeText(baseContext,"Please fill all the fields",Toast.LENGTH_SHORT).show()
        }

        auth.createUserWithEmailAndPassword(inputemail,inputpassword)
            .addOnCompleteListener(this){ task ->
                if (task.isSuccessful){
                    val intent = Intent(this, MainActivity::class.java)
                    startActivity(intent)
                    Toast.makeText(baseContext,"Succes",Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(baseContext,"Authentication Failed",Toast.LENGTH_SHORT).show()
                }
            }
            .addOnFailureListener{
                Toast.makeText(this, "Error occured ${it.localizedMessage}", Toast.LENGTH_SHORT).show()
            }
    }
}