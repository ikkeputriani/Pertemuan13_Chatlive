import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { App } from './app';
import { ChatService } from './chat.service';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        {
          provide: ChatService,
          useValue: {
            status$: of('connected'),
            messages$: of([]),
            errorMessage$: of(null),
            connect: () => Promise.resolve(),
          },
        },
      ],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render the ChatLive workspace', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.brand')?.textContent).toContain('ChatLive');
    expect(compiled.querySelector('h2')?.textContent).toContain('Ruang Umum');
  });
});
