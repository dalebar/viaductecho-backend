package com.viaductecho.android.ui.main

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.viaductecho.android.data.repository.ArticleRepository
import com.viaductecho.android.utils.Resource
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MainViewModel @Inject constructor(
    private val repository: ArticleRepository
) : ViewModel() {

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _connectionStatus = MutableLiveData<ConnectionStatus>()
    val connectionStatus: LiveData<ConnectionStatus> = _connectionStatus

    init {
        checkConnectionStatus()
    }

    fun checkConnectionStatus() {
        viewModelScope.launch {
            _isLoading.value = true

            when (val result = repository.getHealth()) {
                is Resource.Success -> {
                    _connectionStatus.value = if (result.data?.databaseConnected == true) {
                        ConnectionStatus.ONLINE
                    } else {
                        ConnectionStatus.SERVER_ISSUE
                    }
                }
                is Resource.Error -> {
                    _connectionStatus.value = ConnectionStatus.OFFLINE
                }
                is Resource.Loading -> {
                    // Handle loading state
                }
            }

            _isLoading.value = false
        }
    }

    enum class ConnectionStatus {
        ONLINE,
        OFFLINE,
        SERVER_ISSUE
    }
}
