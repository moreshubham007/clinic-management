import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export function ErrorMessage({ message }: { message: string }) {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: '#ffebee',
    margin: 16,
    borderRadius: 8
  },
  text: {
    color: '#c62828'
  }
}); 