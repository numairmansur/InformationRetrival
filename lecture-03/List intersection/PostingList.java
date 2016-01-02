// Copyright 2015, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Hannah Bast <bast@cs.uni-freiburg.de>.

import java.util.ArrayList;

/**
 * A posting list, with pairs doc id, score (both ints).
 */
public class PostingList {

  /**
   * Create from given ids and scores. Repeat given number of times with given
   * offset for the repetitions.
   */
  public PostingList(ArrayList<Integer> ids, ArrayList<Integer> scores,
                     int numRepeats, int offset) {
    int n = ids.size();
    this.ids = new int[n * numRepeats];
    this.scores = new int[n * numRepeats];
    // this.ids = new ArrayList<Integer>(n * numRepeats);
    // this.scores = new ArrayList<Integer>(n * numRepeats);
    for (int k = 0; k < numRepeats; k++) {
      for (int i = 0; i < n; i++) {
        this.ids[i + k * n] = ids.get(i) + k * offset;
        this.scores[i + k * n] = scores.get(i);
      }
    }
  }

  /**
   * Store as ArrayList internally.
   */
  public int ids[];
  public int scores[];
  // public ArrayList<Integer> ids;
  // public ArrayList<Integer> scores;
}