import { View, StyleSheet, ScrollView } from 'react-native';
import { Surface, Text, Avatar, Button, Card } from 'react-native-paper';
import { useLocalSearchParams } from 'expo-router';

export default function DoctorProfileScreen() {
  const { id } = useLocalSearchParams();
  // In real app, fetch doctor data using id

  return (
    <Surface style={styles.container}>
      <ScrollView>
        <View style={styles.header}>
          <Avatar.Image
            size={100}
            source={{ uri: 'https://picsum.photos/200' }}
          />
          <Text variant="headlineMedium" style={styles.name}>Dr. Smith</Text>
          <Text variant="bodyLarge">Cardiologist</Text>
          
          <View style={styles.stats}>
            <View style={styles.stat}>
              <Text variant="headlineSmall">150+</Text>
              <Text variant="bodySmall">Patients</Text>
            </View>
            <View style={styles.stat}>
              <Text variant="headlineSmall">10+</Text>
              <Text variant="bodySmall">Years Exp.</Text>
            </View>
            <View style={styles.stat}>
              <Text variant="headlineSmall">4.9</Text>
              <Text variant="bodySmall">Rating</Text>
            </View>
          </View>

          <Button mode="contained" style={styles.button}>
            Book Appointment
          </Button>
        </View>

        <Card style={styles.section}>
          <Card.Content>
            <Text variant="titleMedium">About</Text>
            <Text variant="bodyMedium" style={styles.about}>
              Experienced cardiologist specializing in preventive cardiology and heart disease management.
            </Text>
          </Card.Content>
        </Card>

        <Card style={styles.section}>
          <Card.Content>
            <Text variant="titleMedium">Available Time Slots</Text>
            <View style={styles.timeSlots}>
              {/* Add time slots here */}
            </View>
          </Card.Content>
        </Card>
      </ScrollView>
    </Surface>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    alignItems: 'center',
    padding: 20,
  },
  name: {
    marginTop: 10,
  },
  stats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginVertical: 20,
  },
  stat: {
    alignItems: 'center',
  },
  button: {
    marginTop: 10,
    width: '80%',
  },
  section: {
    margin: 10,
  },
  about: {
    marginTop: 10,
  },
  timeSlots: {
    marginTop: 10,
  },
}); 