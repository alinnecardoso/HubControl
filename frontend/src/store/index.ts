import { configureStore, createSlice } from '@reduxjs/toolkit';

// Slice temporário para evitar erro do Redux
const appSlice = createSlice({
  name: 'app',
  initialState: { initialized: true },
  reducers: {
    setInitialized: (state, action) => {
      state.initialized = action.payload;
    },
  },
});

// Configuração básica do store
export const store = configureStore({
  reducer: {
    app: appSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 