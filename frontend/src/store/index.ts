import { configureStore } from '@reduxjs/toolkit';

// Configuração básica do store
export const store = configureStore({
  reducer: {
    // Reducers serão adicionados aqui
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 