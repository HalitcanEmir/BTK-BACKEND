import DeveloperList from './DeveloperList';
import ProjectSuggestions from './ProjectSuggestions';

export default function DevelopersPage() {
  // Giriş yapan kullanıcının id'sini auth'dan çekmelisin
  const developerId = 1; // örnek
  return (
    <main>
      <h1>Geliştiriciler</h1>
      <DeveloperList />
      <ProjectSuggestions developerId={developerId} />
    </main>
  );
}
