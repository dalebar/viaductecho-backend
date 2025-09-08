package com.viaductecho.android.utils

/**
 * A generic wrapper class for handling different states of data loading
 */
sealed class Resource<T>(
    val data: T? = null,
    val message: String? = null
) {
    class Success<T>(data: T) : Resource<T>(data)
    class Error<T>(message: String, data: T? = null) : Resource<T>(data, message)
    class Loading<T>(data: T? = null) : Resource<T>(data)

    companion object {
        fun <T> success(data: T): Resource<T> = Success(data)
        fun <T> error(message: String, data: T? = null): Resource<T> = Error(message, data)
        fun <T> loading(data: T? = null): Resource<T> = Loading(data)
    }
}