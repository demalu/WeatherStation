package com.example.provaappweatherstation

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class SkyViewActivity: AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.skyview_activity)
        /*val cloud_recived = intent.getStringArrayListExtra("Cloudiness")
        val time_riceved_cloud = intent.getStringArrayListExtra("Time Cloudiness")
        println(cloud_recived)
        println(time_riceved_cloud)*/
    }
}