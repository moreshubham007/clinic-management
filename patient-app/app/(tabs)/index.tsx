import React from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';
import { Surface, Card, Text, Avatar, Button } from 'react-native-paper';
import { StoryCircle } from '@/components/StoryCircle';

const doctors = [
  { id: '1', name: 'Dr. Smith', imageUrl: 'https://picsum.photos/200', specialty: 'Cardiologist' },
  { id: '2', name: 'Dr. Johnson', imageUrl: 'https://picsum.photos/201', specialty: 'Neurologist' },
  // Add more doctors
];

const appointments = [
  {
    id: '1',
    doctor: doctors[0],
    date: new Date(),
    status: 'Upcoming',
    description: 'Regular checkup',
  },
  // Add more appointments
];

export default function HomeScreen() {
  return (
    <Surface style={styles.container}>
      <ScrollView>
        {/* Stories Section */}
        <View style={styles.storiesContainer}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {doctors.map(doctor => (
              <StoryCircle
                key={doctor.id}
                imageUrl={doctor.imageUrl}
                name={doctor.name}
                onPress={() => {}}
              />
            ))}
          </ScrollView>
        </View>

        {/* Feed Section */}
        <View style={styles.feed}>
          {appointments.map(appointment => (
            <Card key={appointment.id} style={styles.card}>
              <Card.Title
                title={appointment.doctor.name}
                subtitle={appointment.doctor.specialty}
                left={props => (
                  <Avatar.Image {...props} source={{ uri: appointment.doctor.imageUrl }} />
                )}
                right={props => (
                  <Button {...props} onPress={() => {}}>More</Button>
                )}
              />
              <Card.Content>
                <Text variant="bodyLarge">
                  Appointment: {appointment.date.toLocaleDateString()}
                </Text>
                <Text variant="bodyMedium">{appointment.description}</Text>
                <Text variant="bodyMedium" style={styles.status}>
                  Status: {appointment.status}
                </Text>
              </Card.Content>
              <Card.Actions>
                <Button>Reschedule</Button>
                <Button>Cancel</Button>
              </Card.Actions>
            </Card>
          ))}
        </View>
      </ScrollView>
    </Surface>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  storiesContainer: {
    paddingVertical: 10,
    borderBottomWidth: 0.5,
    borderBottomColor: '#ccc',
  },
  feed: {
    padding: 10,
  },
  card: {
    marginBottom: 15,
  },
  status: {
    marginTop: 8,
    color: '#2f95dc',
  },
});
