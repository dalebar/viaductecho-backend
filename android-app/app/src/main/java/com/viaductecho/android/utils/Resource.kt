package com.viaductecho.android.utils

/**
 * A generic wrapper class for handling different states of data loading
 */
sealed class Resource<T> {
    data class Success<T>(val data: T) : Resource<T>()
    data class Error<T>(val message: String, val data: T? = null) : Resource<T>()
    data class Loading<T>(val data: T? = null) : Resource<T>()

    companion object {
        fun <T> success(data: T): Resource<T> = Success(data)
        fun <T> error(message: String, data: T? = null): Resource<T> = Error(message, data)
        fun <T> loading(data: T? = null): Resource<T> = Loading(data)
    }
}
