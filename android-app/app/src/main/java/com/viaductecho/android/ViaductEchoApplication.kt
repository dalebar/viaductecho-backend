package com.viaductecho.android

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class ViaductEchoApplication : Application() {
    
    override fun onCreate() {
        super.onCreate()
    }
}