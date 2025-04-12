import React from 'react';
import { View, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { Text } from 'react-native-paper';

type StoryCircleProps = {
  imageUrl: string;
  name: string;
  onPress: () => void;
};

export const StoryCircle = ({ imageUrl, name, onPress }: StoryCircleProps) => (
  <TouchableOpacity style={styles.container} onPress={onPress}>
    <View style={styles.imageContainer}>
      <Image source={{ uri: imageUrl }} style={styles.image} />
    </View>
    <Text variant="labelSmall" style={styles.name}>{name}</Text>
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginHorizontal: 8,
  },
  imageContainer: {
    width: 70,
    height: 70,
    borderRadius: 35,
    borderWidth: 2,
    borderColor: '#E1306C',
    padding: 2,
  },
  image: {
    width: '100%',
    height: '100%',
    borderRadius: 33,
  },
  name: {
    marginTop: 4,
    textAlign: 'center',
  },
}); 