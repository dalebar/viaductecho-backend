package com.viaductecho.android.utils

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build
import androidx.core.content.ContextCompat
import java.text.SimpleDateFormat
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.util.*

/**
 * Extension functions for common operations
 */

// Network connectivity check
fun Context.isNetworkAvailable(): Boolean {
    val connectivityManager = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false

        return when {
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> true
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> true
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> true
            else -> false
        }
    } else {
        @Suppress("DEPRECATION")
        val networkInfo = connectivityManager.activeNetworkInfo ?: return false
        @Suppress("DEPRECATION")
        return networkInfo.isConnected
    }
}

// Image loading is handled by ImageLoadingUtils.kt

// Date formatting utilities
object DateUtils {

    private const val API_DATE_FORMAT = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS+00:00"
    private const val API_DATE_FORMAT_ALT = "yyyy-MM-dd'T'HH:mm:ss+00:00"
    private const val DISPLAY_DATE_FORMAT = "MMM dd, yyyy"
    private const val DISPLAY_TIME_FORMAT = "HH:mm"

    fun formatRelativeTime(dateString: String?): String {
        if (dateString.isNullOrBlank()) return ""

        return try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val instant = Instant.parse(dateString.replace("+00:00", "Z"))
                val publishedTime = LocalDateTime.ofInstant(instant, ZoneId.systemDefault())
                val now = LocalDateTime.now()

                val minutesAgo = ChronoUnit.MINUTES.between(publishedTime, now)
                val hoursAgo = ChronoUnit.HOURS.between(publishedTime, now)
                val daysAgo = ChronoUnit.DAYS.between(publishedTime, now)

                when {
                    minutesAgo < 1 -> "Just now"
                    minutesAgo < 60 -> "${minutesAgo}m ago"
                    hoursAgo < 24 -> "${hoursAgo}h ago"
                    daysAgo < 7 -> "${daysAgo}d ago"
                    else -> publishedTime.format(DateTimeFormatter.ofPattern(DISPLAY_DATE_FORMAT))
                }
            } else {
                // Fallback for API < 26
                formatDateLegacy(dateString)
            }
        } catch (e: Exception) {
            ""
        }
    }

    fun formatDisplayDate(dateString: String?): String {
        if (dateString.isNullOrBlank()) return ""

        return try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val instant = Instant.parse(dateString.replace("+00:00", "Z"))
                val localDateTime = LocalDateTime.ofInstant(instant, ZoneId.systemDefault())
                localDateTime.format(DateTimeFormatter.ofPattern("$DISPLAY_DATE_FORMAT • $DISPLAY_TIME_FORMAT"))
            } else {
                formatDateLegacy(dateString)
            }
        } catch (e: Exception) {
            dateString
        }
    }

    @Suppress("DEPRECATION")
    private fun formatDateLegacy(dateString: String): String {
        return try {
            val inputFormat = SimpleDateFormat(API_DATE_FORMAT, Locale.getDefault())
            val outputFormat = SimpleDateFormat(DISPLAY_DATE_FORMAT, Locale.getDefault())
            val date = inputFormat.parse(dateString) ?: return dateString
            outputFormat.format(date)
        } catch (e: Exception) {
            try {
                val inputFormat = SimpleDateFormat(API_DATE_FORMAT_ALT, Locale.getDefault())
                val outputFormat = SimpleDateFormat(DISPLAY_DATE_FORMAT, Locale.getDefault())
                val date = inputFormat.parse(dateString) ?: return dateString
                outputFormat.format(date)
            } catch (e: Exception) {
                dateString
            }
        }
    }
}
