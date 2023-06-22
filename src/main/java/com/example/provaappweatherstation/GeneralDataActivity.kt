package com.example.provaappweatherstation

import android.content.Intent
import android.os.Bundle
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class GeneralDataActivity: AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.generaldata_activity)
       /* val humidity_recived = intent.getStringArrayListExtra("Humidity")
        val time_riceved_hum = intent.getStringArrayListExtra("TempoHumidity")
        val co2_recived = intent.getStringArrayListExtra("Co2")
        val time_riceved_co2 = intent.getStringArrayListExtra("Time Co2")*/

        val hum_btn = findViewById<ImageView>(R.id.humIMG)
        hum_btn.setOnClickListener {
            val intent = Intent(this, HumidityActivity::class.java)
            startActivity(intent)
        }


    }
}