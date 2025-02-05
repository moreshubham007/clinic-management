package com.hospital.app.api

import com.google.gson.TypeAdapter
import com.google.gson.stream.JsonReader
import com.google.gson.stream.JsonToken
import com.google.gson.stream.JsonWriter

class ListTypeAdapter : TypeAdapter<List<*>>() {
    override fun write(out: JsonWriter, value: List<*>?) {
        if (value == null) {
            out.nullValue()
            return
        }
        out.beginArray()
        for (item in value) {
            if (item == null) {
                out.nullValue()
            } else {
                out.value(item.toString())
            }
        }
        out.endArray()
    }

    override fun read(reader: JsonReader): List<*>? {
        if (reader.peek() == JsonToken.NULL) {
            reader.nextNull()
            return null
        }
        
        // If we get a string instead of an array, try to parse it
        if (reader.peek() == JsonToken.STRING) {
            val value = reader.nextString()
            // If it's an empty string or "null", return empty list
            if (value.isBlank() || value == "null") {
                return emptyList<Any>()
            }
            // Try to parse the string as a single item list
            return listOf(value)
        }
        
        // Handle normal array
        val list = mutableListOf<Any>()
        reader.beginArray()
        while (reader.hasNext()) {
            when (reader.peek()) {
                JsonToken.NULL -> {
                    reader.nextNull()
                    list.add("")
                }
                JsonToken.STRING -> list.add(reader.nextString())
                JsonToken.NUMBER -> list.add(reader.nextDouble())
                JsonToken.BOOLEAN -> list.add(reader.nextBoolean())
                else -> reader.skipValue()
            }
        }
        reader.endArray()
        return list
    }
} 