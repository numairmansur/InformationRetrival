// Copyright 2015, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Hannah Bast <bast@cs.uni-freiburg.de>.

import java.io.IOException;
import java.util.InputMismatchException;
import java.util.Scanner;

/**
 *
 */
public class ListIntersectionMain {
  public static void main(String[] args) throws IOException {
    Scanner in = new Scanner(System.in);
    System.out.println("Select a posting lists combination:");
    System.out.println("\t[1]: \"film\" + \"comedy\"");
    System.out.println("\t[2]: \"film\" + \"2015\"");
    System.out.println("\t[3]: \"2015\" + \"comedy\"");

    int listSelection = 1;
    try {
      System.out.print("> ");
      listSelection = in.nextInt();
    } catch (InputMismatchException e) {
      System.out.println("You should enter an integer value!");
      System.exit(0);
    }

    String listNames[] = {"film", "comedy"};
    if (listSelection == 1) {
      listNames = new String[] {"film", "comedy"};
    } else if (listSelection == 2) {
      listNames = new String[] {"film", "2015"};
    } else if (listSelection == 3) {
      listNames = new String[] {"2015", "comedy"};
    } else {
      System.out.println("You have selected the wrong option!");
      System.exit(0);
    }

    int m = listNames.length;
    ListIntersection li = new ListIntersection();

    // Read lists.
    PostingList lists[] = new PostingList[m];
    System.out.println();

    for (int i = 0; i < m; i++) {
      System.out.print("Reading list \"" + listNames[i] + "\" ... ");
      System.out.flush();
      String fileName = "postinglists/" + listNames[i] + ".txt";
      // lists[i] = li.readPostingList(fileName, 1, 0);
      lists[i] = li.readPostingList(fileName, 100, 200 * 1000);
      System.out.println("done, size = " +  lists[i].ids.length);
    }

    System.out.println("\nSelect a posting lists intersection method:");
    System.out.println("\t[1]: Linear (time) Search");
    System.out.println("\t[2]: Binary Search");
    System.out.println("\t[3]: Gallop Search");
    System.out.println("\t[4]: Skip Pointers Search");

    int intersectionSelection = 0;
    try {
      System.out.print("> ");
      intersectionSelection = in.nextInt();
    } catch (InputMismatchException e) {
      System.out.println("You should enter an integer value!");
      System.exit(0);
    }
    System.out.println();

    String method = "intersect";
    if (intersectionSelection == 1) {
      method = "intersect";
    } else if (intersectionSelection == 2) {
      method = "intersectBinarySearch";
    } else if (intersectionSelection == 3) {
      method = "intersectGallopSearch";
    } else if (intersectionSelection == 4) {
      method = "skipPointers";
    } else {
      System.out.println("You have selected the wrong option!");
      System.exit(0);
    }

    System.out.println("Wait...");

    // Performance test.
    // for (int i = 0; i < m; i++) {
    // li.performanceTest(lists[i], listNames[i]); }

    long totalTime = 0;
    int numOfTests = 10;

    if (lists[1].ids.length < lists[0].ids.length) {
      PostingList temp = lists[0];
      lists[0] = lists[1];
      lists[1] = temp;
    }

    // Performance test for our intersect.
    for (int run = 0; run < numOfTests; run++) {
      // System.out.print("Intersecting \"" + listNames[0] + "\" with \"" +
      // listNames[1] + "\" ...");
      // System.out.flush();
      long time1 = System.currentTimeMillis();

      try {
        li.getClass().getMethod(method, PostingList.class,
          PostingList.class).invoke(li, lists[0], lists[1]);
      } catch (Exception e) {
        System.out.print("\n Some Error Occured");
        System.exit(0);
      }

      long time2 = System.currentTimeMillis();
      long delta = time2 - time1;
      // System.out.println("done in " + delta + "ms");
      totalTime += delta;
    }
    System.out.print("\nIntersecting \"" + listNames[0] + "\" with \""
      + listNames[1] + "\": ");
    System.out.println("average time is " + (totalTime / numOfTests) + "ms");
  }
}
