import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Suspense, lazy } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { Layout } from "./components/layout/Layout";
import { PageTransition } from "./components/layout/PageTransition";
import { PageSpinner } from "./components/common/PageSpinner";
import { HomePage } from "./pages/HomePage";

const SearchResultsPage = lazy(() =>
  import("./pages/SearchResultsPage").then((m) => ({
    default: m.SearchResultsPage,
  }))
);
const StationsPage = lazy(() =>
  import("./pages/StationsPage").then((m) => ({ default: m.StationsPage }))
);
const StationDetailPage = lazy(() =>
  import("./pages/StationDetailPage").then((m) => ({
    default: m.StationDetailPage,
  }))
);
const TrainsPage = lazy(() =>
  import("./pages/TrainsPage").then((m) => ({ default: m.TrainsPage }))
);
const TrainDetailPage = lazy(() =>
  import("./pages/TrainDetailPage").then((m) => ({
    default: m.TrainDetailPage,
  }))
);
const RoutesPage = lazy(() =>
  import("./pages/RoutesPage").then((m) => ({ default: m.RoutesPage }))
);
const RouteDetailPage = lazy(() =>
  import("./pages/RouteDetailPage").then((m) => ({
    default: m.RouteDetailPage,
  }))
);
const AnalyticsPage = lazy(() =>
  import("./pages/AnalyticsPage").then((m) => ({ default: m.AnalyticsPage }))
);
const LoginPage = lazy(() =>
  import("./pages/LoginPage").then((m) => ({ default: m.LoginPage }))
);
const RegisterPage = lazy(() =>
  import("./pages/RegisterPage").then((m) => ({ default: m.RegisterPage }))
);
const NotFoundPage = lazy(() =>
  import("./pages/NotFoundPage").then((m) => ({ default: m.NotFoundPage }))
);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <BrowserRouter>
            <Layout>
              <PageTransition>
                <Suspense fallback={<PageSpinner />}>
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/search" element={<SearchResultsPage />} />
                    <Route path="/stations" element={<StationsPage />} />
                    <Route
                      path="/stations/:id"
                      element={<StationDetailPage />}
                    />
                    <Route path="/trains" element={<TrainsPage />} />
                    <Route
                      path="/trains/:id"
                      element={<TrainDetailPage />}
                    />
                    <Route path="/routes" element={<RoutesPage />} />
                    <Route
                      path="/routes/:id"
                      element={<RouteDetailPage />}
                    />
                    <Route path="/analytics" element={<AnalyticsPage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="*" element={<NotFoundPage />} />
                  </Routes>
                </Suspense>
              </PageTransition>
            </Layout>
          </BrowserRouter>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
