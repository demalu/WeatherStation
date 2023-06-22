package com.example.provaappweatherstation

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class SunIrradiationActivity: AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.sunirradiation_activity)
        val irr_recived = intent.getStringArrayListExtra("Irradiation")
        val time_riceved_irr = intent.getStringArrayListExtra("Time Irradiation")
        println(irr_recived)
        println(time_riceved_irr)
    }
}
