import { AfterViewChecked, Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from './git.service';


@Component({
  selector: 'app-commit',
  templateUrl: `./diff.component.html`,
})
export class CommitComponent implements OnDestroy, OnInit, AfterViewChecked {

  public data;
  private projectId;
  private hash;
  private filename: string;

  constructor(private route: ActivatedRoute, private gitService: GitService, private router: Router) {}

  ngOnInit() {
    this.route.paramMap
        .switchMap((params: ParamMap) => {
          this.gitService.setCommitHash(params.get('hash'));
          document.querySelector('.autoscroll-right').scrollTop = 0;
          this.projectId = this.route.parent.parent.snapshot.params['id'];
          this.hash = params.get('hash');
          return this.gitService.getDiff(
            this.projectId, this.hash);
        }).subscribe(data => {
          console.log('subscribe', data);
          this.data = data;
        });

        this.route.fragment.subscribe((hash: string) => {
          this.filename = hash ? hash : null;
          // NOTE: will have no effect after the init, but will scroll when clicking on the link.
          this.scrollToAnchor();
        });
  }

  scrollToAnchor() {
    if (this.filename) {
      const elt: HTMLElement = document.getElementById(this.filename);
      if (elt) {
        elt.scrollIntoView();
        this.filename = null;
        return true;
      }
    }
    return false;
  }

  ngAfterViewChecked() {
    this.scrollToAnchor();
  }

  expand(line, path, lines, d) {
    // TODO: we don't need lines and d since d contains lines
    const index = lines.indexOf(line);
    this.gitService.getContextDiff(this.projectId, this.hash, path, line['context_data']
                                  ).subscribe(res => {
      d.lines.splice(index, 1, ...res as Array<any>);
    });
    return false;
  }

  ngOnDestroy() {
    this.gitService.setCommitHash(null);
  }

  close() {
    this.router.navigate([{outlets: {commit: null}} ], {relativeTo: this.route.parent});
  }

}
